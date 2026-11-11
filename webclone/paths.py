"""URL -> yerel dosya yolu eşlemesi.

Windows ve Linux çapraz platform uyumluluğu:
  - Windows ayrılmış aygıt adları (CON, PRN, AUX, NUL, COM1-9, LPT1-9) koruması
  - Windows geçersiz karakterleri ve MAX_PATH sınırları temizliği
  - HTML ve CSS içinde her zaman standart web bölü işaretleri (/) kullanımı
"""
from __future__ import annotations

import hashlib
import posixpath
import re
import threading
from urllib.parse import unquote, urlsplit

KIND_DIRS = {
    "css": "assets/css",
    "js": "assets/js",
    "img": "assets/img",
    "font": "assets/fonts",
    "media": "assets/media",
    "other": "assets/files",
}

DEFAULT_EXT = {"css": ".css", "js": ".js"}

EXT_KIND: dict[str, str] = {}
for _kind, _exts in {
    "css": [".css"],
    "js": [".js", ".mjs", ".cjs"],
    "img": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico",
            ".bmp", ".tif", ".tiff", ".apng", ".jfif", ".cur"],
    "font": [".woff", ".woff2", ".ttf", ".otf", ".eot"],
    "media": [".mp4", ".webm", ".ogg", ".ogv", ".mp3", ".wav", ".m4a", ".mov",
              ".aac", ".flac", ".vtt", ".m3u8", ".ts", ".mpd"],
    "other": [".json", ".xml", ".pdf", ".txt", ".webmanifest", ".map", ".wasm",
              ".csv", ".doc", ".docx", ".xls", ".xlsx"],
}.items():
    for _e in _exts:
        EXT_KIND[_e] = _kind

# Sayfa (HTML) olarak takip edilecek link uzantıları
PAGE_EXTS = {"", ".html", ".htm", ".php", ".asp", ".aspx", ".jsp", ".cfm", ".shtml", ".xhtml"}

# Windows için ayrılmış dosya/aygıt adları
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

_UNSAFE = re.compile(r"[^A-Za-z0-9._\-~@+]")


def short_hash(text: str, n: int = 8) -> str:
    return hashlib.sha1(text.encode("utf-8", "surrogatepass")).hexdigest()[:n]


def safe_segment(seg: str, maxlen: int = 70) -> str:
    """Dosya sistemi (Windows & Linux) ve URL için güvenli bir yol parçası üretir."""
    # Güvensiz karakterleri alt çizgiye çevir
    cleaned = _UNSAFE.sub("_", seg).strip(" .") or "_"

    # Windows ayrılmış aygıt adlarını engelle (örn. aux.html -> _aux.html)
    stem, ext = posixpath.splitext(cleaned)
    if stem.upper() in WINDOWS_RESERVED:
        cleaned = f"_{cleaned}"
        stem = f"_{stem}"

    # Çok uzun isimleri hash ile kısalt (Windows MAX_PATH aşılmasın)
    if len(cleaned) > maxlen:
        ext = ext[:10]
        cleaned = f"{stem[: maxlen - len(ext) - 9]}_{short_hash(seg)}{ext}"

    # Sonunda boşluk veya nokta kalamaz (Windows dosya sistemi hatası)
    return cleaned.strip(" .") or "_"


def url_ext(url: str) -> str:
    return posixpath.splitext(unquote(urlsplit(url).path))[1].lower()


def guess_kind(url: str, hint: str | None = None) -> str:
    """Önce uzantıya, yoksa bağlamdan gelen ipucuna göre varlık türünü belirler."""
    return EXT_KIND.get(url_ext(url), hint or "other")


def bare_host(url_or_host: str) -> str:
    host = urlsplit(url_or_host).hostname if "//" in url_or_host else url_or_host
    host = (host or "").lower()
    return host[4:] if host.startswith("www.") else host


def _with_query_hash(name: str, query: str) -> str:
    if not query:
        return name
    stem, ext = posixpath.splitext(name)
    return f"{stem}_{short_hash(query)}{ext}"


def page_path(url: str) -> str:
    """Sayfa URL'sini yerel .html yoluna çevirir.

    /            -> index.html
    /hakkinda    -> hakkinda.html
    /blog/       -> blog/index.html
    /urun.php?id=3 -> urun.php_<hash>.html
    """
    parts = urlsplit(url)
    path = unquote(parts.path) or "/"
    if path.endswith("/"):
        path += "index.html"
    segs = [safe_segment(s) for s in path.split("/") if s and s not in (".", "..")]
    name = segs[-1] if segs else "index.html"
    if posixpath.splitext(name)[1].lower() not in (".html", ".htm"):
        name += ".html"
    if segs:
        segs[-1] = _with_query_hash(name, parts.query)
    else:
        segs = [_with_query_hash(name, parts.query)]
    return "/".join(segs)


def _asset_candidate(url: str, kind: str, layout: str, root_host: str) -> str:
    parts = urlsplit(url)
    path = unquote(parts.path)
    raw_segs = [s for s in path.split("/") if s and s not in (".", "..")]

    if layout == "mirror":
        segs = [safe_segment(s) for s in raw_segs] or ["index"]
        host = bare_host(parts.hostname or "")
        if host != root_host:
            segs = ["_external", safe_segment(parts.hostname or "host")] + segs
    else:
        name = safe_segment(raw_segs[-1]) if raw_segs else "file"
        segs = KIND_DIRS.get(kind, KIND_DIRS["other"]).split("/") + [name]

    name = segs[-1]
    if not posixpath.splitext(name)[1] and kind in DEFAULT_EXT:
        name += DEFAULT_EXT[kind]
    segs[-1] = _with_query_hash(name, parts.query)
    return "/".join(segs)


class PathRegistry:
    """URL'lere benzersiz yerel yollar atar (thread-safe)."""

    def __init__(self, layout: str, root_host: str):
        self.layout = layout
        self.root_host = root_host
        self._by_url: dict[str, str] = {}
        self._taken: set[str] = set()
        self._lock = threading.Lock()

    def lookup(self, url: str) -> str | None:
        with self._lock:
            return self._by_url.get(url)

    def alias(self, url: str, path: str) -> None:
        with self._lock:
            self._by_url.setdefault(url, path)

    def _reserve(self, url: str, candidate: str) -> tuple[str, bool]:
        with self._lock:
            if url in self._by_url:
                return self._by_url[url], False
            path = candidate
            if path.lower() in self._taken:
                stem, ext = posixpath.splitext(candidate)
                path = f"{stem}_{short_hash(url)}{ext}"
            self._taken.add(path.lower())
            self._by_url[url] = path
            return path, True

    def reserve_page(self, url: str) -> tuple[str, bool]:
        return self._reserve(url, page_path(url))

    def reserve_asset(self, url: str, kind: str) -> tuple[str, bool]:
        return self._reserve(url, _asset_candidate(url, kind, self.layout, self.root_host))


def relative(target: str, from_file: str) -> str:
    """from_file konumundan target dosyasına göreceli posix yolu."""
    start = posixpath.dirname(from_file) or "."
    return posixpath.relpath(target, start)
