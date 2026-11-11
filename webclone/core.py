"""Klonlama motoru. CLI ve GUI bu modüldeki `Cloner` sınıfını kullanır.

Gelişmiş Özellikler:
  - Yüksek hızlı eşzamanlı indirme ve dizin önbellekleme
  - Tam gizlilik ve anonimlik (StealthManager, proxy, UA rotasyonu, insan gecikmesi)
  - Hedef web sitesi istihbaratı ve otomatik HTML/JSON rapor üretimi (ReconCollector)
  - Zenginleştirilmiş varlık tespiti (OG görselleri, manifest, SPA JSON blokları)
  - Windows & Linux çapraz platform dosya sistemi uyumluluğu
"""
from __future__ import annotations

import json
import posixpath
import re
import threading
import time
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .browser import FetchResponse, fetch_via_chromium, fetch_via_curl
from .paths import (
    EXT_KIND, PAGE_EXTS, PathRegistry, bare_host, guess_kind, relative, url_ext,
)
from .recon import ReconCollector, ReconReport
from .rewrite import (
    DROP, HtmlRewriter, build_srcset, decode, detect_encoding, encode,
    parse_srcset, rewrite_css,
)
from .server import NAV_FIX_SCRIPT
from .stealth import StealthManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_SKIP_PREFIXES = ("data:", "javascript:", "mailto:", "tel:", "#", "blob:", "about:", "sms:")

# (etiket, nitelik) -> varlık türü ipucu
ASSET_ATTRS = {
    ("img", "src"): "img", ("img", "data-src"): "img", ("img", "data-lazy-src"): "img",
    ("img", "data-original"): "img", ("img", "lowsrc"): "img",
    ("source", "src"): "media", ("video", "src"): "media", ("audio", "src"): "media",
    ("video", "poster"): "img", ("track", "src"): "media",
    ("script", "src"): "js", ("input", "src"): "img",
    ("embed", "src"): "other", ("object", "data"): "other",
    ("image", "href"): "img", ("image", "xlink:href"): "img",
    ("use", "href"): "img", ("use", "xlink:href"): "img",
    ("body", "background"): "img", ("table", "background"): "img", ("td", "background"): "img",
    ("iframe", "src"): "other",
}
BG_ATTRS = {"data-bg", "data-background", "data-background-image", "data-bg-src"}
SRCSET_ATTRS = {"srcset", "data-srcset", "imagesrcset", "data-lazy-srcset", "data-bgset"}
ABSOLUTIZE_ATTRS = {"href", "src", "action", "formaction", "cite", "data"}
RESOURCE_SECURITY_ATTRS = {"integrity", "crossorigin"}

ICON_RELS = {"icon", "shortcut", "shortcut icon", "apple-touch-icon", "apple-touch-icon-precomposed", "mask-icon"}
PRELOAD_AS = {
    "style": "css", "script": "js", "font": "font", "image": "img",
    "audio": "media", "video": "media", "track": "media", "fetch": "other",
}

# JSON içindeki varlık URL'lerini yakalamak için hızlı regex
_JSON_ASSET_RE = re.compile(
    r"""(?P<quote>["'])(?P<url>(?:https?://[^"'\s]+|/[^"'\s]+\.(?:png|jpg|jpeg|webp|avif|svg|ico|gif|css|js|woff2|woff|ttf|mp4|webm|json)))["']""",
    re.IGNORECASE,
)


@dataclass
class CloneOptions:
    depth: int = 0                  # 0 = sadece verilen sayfa, 1 = + linklediği sayfalar ...
    max_pages: int = 50
    workers: int = 16               # Yüksek performanslı indirme için varsayılan 16
    timeout: float = 12.0
    retries: int = 1
    layout: str = "organized"       # "organized" | "mirror"
    external_assets: bool = True    # CDN gibi başka alan adlarındaki varlıkları da indir
    verify_ssl: bool = False        # Sertifika hatalarında takılmamak için
    render_js: bool = False         # Gerçek Chromium ile sayfaları render et
    # Anonimlik & Gizlilik
    user_agent_profile: str = "random"
    rotate_ua: bool = False
    proxy: str | None = None
    referer_mode: str = "google"
    min_delay: float = 0.0
    max_delay: float = 0.0
    # İstihbarat & Bilgi Toplama
    collect_recon: bool = True
    # Varlık Filtreleme
    download_images: bool = True
    download_styles: bool = True
    download_scripts: bool = True
    download_fonts: bool = True
    download_media: bool = True
    download_documents: bool = True


@dataclass
class CloneResult:
    url: str
    output_dir: Path
    index_file: Path | None
    pages: list[str] = field(default_factory=list)
    assets_ok: int = 0
    failed: list[tuple[str, str]] = field(default_factory=list)
    elapsed: float = 0.0
    cancelled: bool = False
    total_bytes: int = 0
    recon_report: ReconReport | None = None
    recon_json: Path | None = None
    recon_html: Path | None = None
    asset_stats: dict[str, int] = field(default_factory=dict)


EventCallback = Callable[[str, dict[str, Any]], None]


class CloneCancelled(Exception):
    pass


class Cloner:
    """Bir web sayfasını ve bağlantılı varlıklarını yerel klasöre kopyalar.

    Olaylar (on_event(ad, veri)):
      start, recon_done, page_start, page_done, page_failed,
      asset_queued, asset_done, asset_failed, finished
    """

    def __init__(
        self,
        url: str,
        output_dir: str | Path | None = None,
        options: CloneOptions | None = None,
        on_event: EventCallback | None = None,
        cancel_event: threading.Event | None = None,
    ):
        url = url.strip()
        if "://" not in url:
            url = "https://" + url
        self.start_url = url
        self.opts = options or CloneOptions()
        self.on_event = on_event or (lambda name, data: None)
        self.cancel_event = cancel_event or threading.Event()
        self.output_dir = Path(output_dir) if output_dir else Path("output") / (
            urlsplit(url).hostname or "site")

        self.stealth = StealthManager(
            profile_name=self.opts.user_agent_profile,
            proxy=self.opts.proxy,
            referer_mode=self.opts.referer_mode,
            min_delay=self.opts.min_delay,
            max_delay=self.opts.max_delay,
            rotate_ua=self.opts.rotate_ua,
        )

        self.session = self._make_session()
        self.registry: PathRegistry | None = None
        self.root_host = bare_host(url)
        self._prefer_curl = False

        self._lock = threading.Lock()
        self._pending: deque[Future] = deque()
        self._executor: ThreadPoolExecutor | None = None
        self._page_queue: deque[tuple[str, int]] = deque()
        self._page_count = 0
        self._assets_total = 0
        self._assets_done = 0
        self._assets_ok = 0
        self._total_bytes = 0
        self._asset_stats: dict[str, int] = {}
        self._created_dirs: set[Path] = set()
        self._failed: list[tuple[str, str]] = []
        self._pages_done: list[str] = []
        self._recon: ReconCollector | None = None

    # ------------------------------------------------------------ Altyapı
    def _make_session(self) -> requests.Session:
        s = requests.Session()
        retry = Retry(
            total=self.opts.retries,
            connect=1,
            read=0,
            status=1,
            backoff_factor=0.2,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        pool_max = max(64, self.opts.workers * 4)
        adapter = HTTPAdapter(max_retries=retry, pool_connections=64, pool_maxsize=pool_max)
        s.mount("http://", adapter)
        s.mount("https://", adapter)

        # Proxy
        proxy_dict = self.stealth.get_proxy_dict()
        if proxy_dict:
            s.proxies.update(proxy_dict)

        s.verify = self.opts.verify_ssl
        return s

    def _emit(self, name: str, **data: Any) -> None:
        try:
            self.on_event(name, data)
        except Exception:  # noqa: BLE001
            pass

    def _check_cancel(self) -> None:
        if self.cancel_event.is_set():
            raise CloneCancelled()

    def _is_localhost(self, url: str) -> bool:
        host = (urlsplit(url).hostname or "").lower()
        return host in ("127.0.0.1", "localhost", "::1")

    def _get(
        self,
        url: str,
        referer: str | None = None,
        is_page: bool = False,
        kind: str = "page",
    ) -> requests.Response | FetchResponse:
        self.stealth.apply_delay()

        # 1. Chromium render seçeneği
        if is_page and self.opts.render_js and not self._is_localhost(url):
            try:
                return fetch_via_chromium(url, timeout=max(20.0, self.opts.timeout), proxy=self.opts.proxy)
            except Exception:  # noqa: BLE001
                pass

        # 2. curl tercihi (Cloudflare / Akamai HTTP/2)
        if self._prefer_curl and not self._is_localhost(url):
            try:
                prof = self.stealth.get_profile()
                return fetch_via_curl(
                    url,
                    referer=referer,
                    timeout=self.opts.timeout,
                    user_agent=prof.user_agent,
                    proxy=self.opts.proxy,
                )
            except Exception:  # noqa: BLE001
                if is_page:
                    return fetch_via_chromium(url, timeout=max(20.0, self.opts.timeout), proxy=self.opts.proxy)
                raise

        # 3. Hızlı requests bağlantısı
        headers = self.stealth.get_headers(url, is_page=is_page, kind=kind, custom_referer=referer)
        req_timeout = (4.0, min(8.0, self.opts.timeout))
        try:
            r = self.session.get(url, timeout=req_timeout, headers=headers)
            r.raise_for_status()
            return r
        except requests.exceptions.SSLError:
            try:
                self.session.verify = False
                r = self.session.get(url, timeout=req_timeout, headers=headers, verify=False)
                r.raise_for_status()
                return r
            except Exception as ssl_exc:  # noqa: BLE001
                last_exc: Exception = ssl_exc
        except Exception as exc:  # noqa: BLE001
            last_exc = exc

        if self._is_localhost(url):
            raise last_exc

        # 4. curl HTTP/2 ile aşmayı dene
        try:
            prof = self.stealth.get_profile()
            resp = fetch_via_curl(
                url,
                referer=referer,
                timeout=self.opts.timeout,
                user_agent=prof.user_agent,
                proxy=self.opts.proxy,
            )
            if isinstance(last_exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                self._prefer_curl = True
            return resp
        except Exception:  # noqa: BLE001
            pass

        # 5. Son çare görünmez Chromium
        if is_page:
            try:
                resp = fetch_via_chromium(url, timeout=max(22.0, self.opts.timeout), proxy=self.opts.proxy)
                self._prefer_curl = True
                return resp
            except Exception:  # noqa: BLE001
                pass

        raise last_exc

    def _write(self, local: str, data: bytes) -> None:
        target = self.output_dir / local
        parent = target.parent
        if parent not in self._created_dirs:
            parent.mkdir(parents=True, exist_ok=True)
            self._created_dirs.add(parent)
        target.write_bytes(data)

    def _fail(self, url: str, err: Exception | str, kind: str) -> None:
        msg = str(err)
        if isinstance(err, requests.HTTPError) and err.response is not None:
            msg = f"HTTP {err.response.status_code}"
        with self._lock:
            self._failed.append((url, msg))
        self._emit(f"{kind}_failed", url=url, error=msg)

    # ------------------------------------------------------------ URL Çözümleme
    @staticmethod
    def _absolutize(raw: str | None, base: str) -> str | None:
        if not raw:
            return None
        raw = raw.strip()
        if not raw or raw.lower().startswith(_SKIP_PREFIXES):
            return None
        absu = urljoin(base, raw)
        return absu if urlsplit(absu).scheme in ("http", "https") else None

    def _same_site(self, url: str) -> bool:
        return bare_host(url) == self.root_host

    def _is_asset_kind_enabled(self, kind: str) -> bool:
        if kind == "img" and not self.opts.download_images:
            return False
        if kind == "css" and not self.opts.download_styles:
            return False
        if kind == "js" and not self.opts.download_scripts:
            return False
        if kind == "font" and not self.opts.download_fonts:
            return False
        if kind == "media" and not self.opts.download_media:
            return False
        if kind == "other" and not self.opts.download_documents:
            return False
        return True

    def asset_ref(self, raw: str, base: str, from_local: str, hint: str) -> str | None:
        """Varlığı indirme kuyruğuna alır ve from_local'e göre göreceli yolunu döndürür."""
        absu = self._absolutize(raw, base)
        if absu is None:
            return None
        url, frag = urldefrag(absu)
        if not self.opts.external_assets and not self._same_site(url):
            return absu
        kind = guess_kind(url, hint)
        if not self._is_asset_kind_enabled(kind):
            return absu

        local, is_new = self.registry.reserve_asset(url, kind)
        if is_new:
            self._schedule(url, local, kind, base)
        return relative(local, from_local) + (f"#{frag}" if frag else "")

    def page_ref(self, raw: str, base: str, from_local: str, depth: int) -> str | None:
        absu = self._absolutize(raw, base)
        if absu is None:
            return None
        url, frag = urldefrag(absu)
        suffix = f"#{frag}" if frag else ""
        if not self._same_site(url) or url_ext(url) not in PAGE_EXTS:
            return absu
        local = self.registry.lookup(url)
        if local is None:
            with self._lock:
                allowed = depth < self.opts.depth and self._page_count < self.opts.max_pages
                if allowed:
                    self._page_count += 1
            if not allowed:
                return absu
            local, _ = self.registry.reserve_page(url)
            self._page_queue.append((url, depth + 1))
        return relative(local, from_local) + suffix

    # ------------------------------------------------------------ Varlık İndirme
    def _schedule(self, url: str, local: str, kind: str, referer: str) -> None:
        with self._lock:
            self._assets_total += 1
            fut = self._executor.submit(self._download_asset, url, local, kind, referer)
            self._pending.append(fut)
        self._emit("asset_queued", url=url, path=local, kind=kind, total=self._assets_total)

    def _download_asset(self, url: str, local: str, kind: str, referer: str) -> None:
        if self.cancel_event.is_set():
            return
        try:
            r = self._get(url, referer=referer, is_page=False, kind=kind)
            data = r.content
            ctype = r.headers.get("Content-Type", "").lower()
            if kind == "css" or "text/css" in ctype:
                text = data.decode("utf-8", "surrogateescape")
                text = rewrite_css(text, lambda u, hint: self.asset_ref(u, r.url, local, hint))
                data = text.encode("utf-8", "surrogateescape")
            self._write(local, data)
            ok = True
            size = len(data)
        except Exception as e:  # noqa: BLE001
            self._fail(url, e, "asset")
            ok = False
            size = 0

        with self._lock:
            self._assets_done += 1
            if ok:
                self._assets_ok += 1
                self._total_bytes += size
                self._asset_stats[kind] = self._asset_stats.get(kind, 0) + 1
            done, total = self._assets_done, self._assets_total

        if ok:
            self._emit("asset_done", url=url, path=local, kind=kind, done=done, total=total, size=size)

    def _wait_assets(self) -> None:
        while True:
            with self._lock:
                if not self._pending:
                    return
                fut = self._pending.popleft()
            fut.result()

    # ------------------------------------------------------------ Sayfa İşleme
    def _process_page(
        self, url: str, depth: int, response: requests.Response | FetchResponse | None = None
    ) -> None:
        local = self.registry.lookup(url) or self.registry.reserve_page(url)[0]
        self._emit("page_start", url=url, path=local, depth=depth)
        try:
            r = response or self._get(url, referer=self.start_url, is_page=True)
        except Exception as e:  # noqa: BLE001
            self._fail(url, e, "page")
            return

        ctype = r.headers.get("Content-Type", "")
        if "html" not in ctype.lower() and ctype:
            self._write(local, r.content)
            self._pages_done.append(local)
            with self._lock:
                self._total_bytes += len(r.content)
            self._emit("page_done", url=url, path=local)
            return

        enc = detect_encoding(r.content, ctype)
        text = decode(r.content, enc)

        # İlk sayfada istihbarat topla
        if depth == 0 and self._recon and self.opts.collect_recon:
            try:
                self._recon.analyze_response(dict(r.headers), getattr(r, "status_code", 200))
                self._recon.analyze_html(text)
                self._emit("recon_done", report=self._recon.report)
            except Exception:  # noqa: BLE001
                pass

        ctx = _PageContext(self, base_url=r.url, local=local, depth=depth)
        out = HtmlRewriter(ctx).rewrite(text)
        out_bytes = encode(out, enc)
        if b"data-page=" in out_bytes and b"data-webclone-nav" not in out_bytes:
            if b"</head>" in out_bytes:
                out_bytes = out_bytes.replace(b"</head>", NAV_FIX_SCRIPT + b"</head>", 1)
            else:
                out_bytes = NAV_FIX_SCRIPT + out_bytes

        self._write(local, out_bytes)
        self._pages_done.append(local)
        with self._lock:
            self._total_bytes += len(out_bytes)
        self._emit("page_done", url=url, path=local)

    def _create_dir_collision_redirects(self) -> None:
        """Hem `sunucu.html` hem de `sunucu/` klasörü varsa `sunucu/index.html` yönlendirmesi oluşturur."""
        for page_rel in list(self._pages_done):
            if not page_rel.endswith(".html") or page_rel.endswith("/index.html") or page_rel == "index.html":
                continue
            dir_rel = page_rel[:-5]
            dir_path = self.output_dir / dir_rel
            idx_path = dir_path / "index.html"
            if dir_path.is_dir() and not idx_path.exists():
                target_name = posixpath.basename(page_rel)
                stub = (
                    "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
                    f"<meta http-equiv=\"refresh\" content=\"0;url=../{target_name}\">"
                    f"<script>location.replace('../{target_name}' + location.search + location.hash);</script>"
                    "</head><body></body></html>"
                )
                idx_path.write_text(stub, encoding="utf-8")

    # ------------------------------------------------------------ Ana Akış
    def run(self) -> CloneResult:
        t0 = time.monotonic()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._emit("start", url=self.start_url, output_dir=str(self.output_dir))
        result = CloneResult(url=self.start_url, output_dir=self.output_dir, index_file=None)

        # İstihbarat başlat
        if self.opts.collect_recon:
            self._recon = ReconCollector(self.start_url, session=self.session)
            self._recon.resolve_dns()

        try:
            first = self._get(self.start_url, is_page=True)
        except Exception as e:  # noqa: BLE001
            self._fail(self.start_url, e, "page")
            result.failed = list(self._failed)
            result.elapsed = time.monotonic() - t0
            self._emit("finished", result=result)
            return result

        final_url = urldefrag(first.url)[0]
        self.root_host = bare_host(final_url)
        self.registry = PathRegistry(self.opts.layout, self.root_host)
        index_local, _ = self.registry.reserve_page(final_url)
        self.registry.alias(urldefrag(self.start_url)[0], index_local)
        self._page_count = 1

        self._executor = ThreadPoolExecutor(max_workers=self.opts.workers, thread_name_prefix="webclone")
        try:
            self._process_page(final_url, 0, first)

            # robots.txt ve sitemap.xml taraması (istihbarat)
            if self.opts.collect_recon and self._recon:
                self._executor.submit(self._recon.fetch_robots_and_sitemaps)

            # Sayfa kuyruğunu işle
            while self._page_queue:
                self._check_cancel()
                url, depth = self._page_queue.popleft()
                self._process_page(url, depth)

            self._check_cancel()
            self._wait_assets()
            self._check_cancel()
            self._create_dir_collision_redirects()

            # İstihbarat raporlarını kaydet
            if self.opts.collect_recon and self._recon:
                self._recon.report.asset_breakdown = dict(self._asset_stats)
                self._recon.report.total_size_bytes = self._total_bytes
                json_p, html_p = self._recon.save_reports(self.output_dir)
                result.recon_report = self._recon.report
                result.recon_json = json_p
                result.recon_html = html_p

        except CloneCancelled:
            result.cancelled = True
        finally:
            self._executor.shutdown(wait=True, cancel_futures=True)

        result.index_file = self.output_dir / index_local
        result.pages = list(self._pages_done)
        result.assets_ok = self._assets_ok
        result.failed = list(self._failed)
        result.total_bytes = self._total_bytes
        result.asset_stats = dict(self._asset_stats)
        result.elapsed = time.monotonic() - t0
        self._emit("finished", result=result)
        return result


class _PageContext:
    """Tek bir HTML sayfasının etiketlerini yeniden yazan handler."""

    def __init__(self, cloner: Cloner, base_url: str, local: str, depth: int):
        self.c = cloner
        self.base_url = base_url
        self.local = local
        self.depth = depth

    def _asset(self, raw: str | None, hint: str) -> str | None:
        if not raw:
            return None
        return self.c.asset_ref(raw, self.base_url, self.local, hint)

    def _css(self, css: str) -> str:
        return rewrite_css(css, lambda u, hint: self._asset(u, hint))

    def on_style_text(self, css: str) -> str:
        return self._css(css)

    def _scan_json_assets(self, raw_json: str) -> str | None:
        """JSON içindeki varlık URL'lerini keşfeder ve yerel dosya yollarına dönüştürür."""
        changed = False

        def repl(m: re.Match) -> str:
            nonlocal changed
            quote = m.group("quote")
            u = m.group("url")
            kind = guess_kind(u, "other")
            new_ref = self._asset(u, kind)
            if new_ref and new_ref != u:
                changed = True
                return f"{quote}{new_ref}{quote}"
            return m.group(0)

        new_json = _JSON_ASSET_RE.sub(repl, raw_json)
        return new_json if changed else None

    def _link_href(self, attrs: dict, href: str):
        rel = set((attrs.get("rel") or "").lower().split())
        as_ = (attrs.get("as") or "").lower()
        type_ = (attrs.get("type") or "").lower()
        if "stylesheet" in rel or type_ == "text/css":
            return self._asset(href, "css"), True
        if rel & ICON_RELS:
            return self._asset(href, "img"), True
        if rel & {"preload", "modulepreload", "prefetch"} and as_ != "document":
            hint = PRELOAD_AS.get(as_, "js" if "modulepreload" in rel else "other")
            return self._asset(href, hint), True
        if "manifest" in rel:
            return self._asset(href, "other"), True
        return self.c._absolutize(href, self.base_url), False

    def on_tag(self, tag: str, attrs: list[tuple[str, str | None]]):
        amap = {k.lower(): v for k, v in attrs}

        if tag == "base":
            if amap.get("href"):
                self.base_url = urljoin(self.base_url, amap["href"])
            return DROP
        if tag == "meta" and (amap.get("http-equiv") or "").lower() == "content-security-policy":
            return DROP

        changed = False
        resource = False
        new_attrs = []
        for name, value in attrs:
            lname = name.lower()
            new = None
            is_res = False
            if value is not None:
                if lname == "style":
                    if "url(" in value.lower() or "image-set(" in value.lower():
                        new = self._css(value)
                elif lname in ("data-page", "data-state") or (tag == "script" and "json" in (amap.get("type") or "")):
                    new = self._scan_json_assets(value)
                elif lname in SRCSET_ATTRS:
                    items = [(self._asset(u, "img") or u, d) for u, d in parse_srcset(value)]
                    new, is_res = build_srcset(items), True
                elif (tag, lname) in ASSET_ATTRS:
                    new, is_res = self._asset(value, ASSET_ATTRS[(tag, lname)]), True
                elif lname in BG_ATTRS:
                    new = self._asset(value, "img")
                elif tag == "meta" and (amap.get("property") or "").lower() in ("og:image", "og:video"):
                    new, is_res = self._asset(value, "img"), True
                elif tag == "meta" and (amap.get("name") or "").lower() in ("twitter:image", "msapplication-tileimage"):
                    new, is_res = self._asset(value, "img"), True
                elif tag == "link" and lname == "href":
                    new, is_res = self._link_href(amap, value)
                elif tag in ("a", "area") and lname == "href":
                    new = self.c.page_ref(value, self.base_url, self.local, self.depth)
                elif lname in ABSOLUTIZE_ATTRS:
                    new = self.c._absolutize(value, self.base_url)

            if new is not None and new != value:
                new_attrs.append((name, new))
                changed = True
                resource = resource or is_res
            else:
                new_attrs.append((name, value))

        if resource:
            new_attrs = [(n, v) for n, v in new_attrs if n.lower() not in RESOURCE_SECURITY_ATTRS]
        return new_attrs if changed else None
