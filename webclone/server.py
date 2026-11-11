"""Akıllı yerel önizleme sunucusu.

Standart `SimpleHTTPRequestHandler`'ın aksine:
  1. `/sunucu` gibi temiz URL'lerde aynı isimde klasör (`sunucu/`) olsa bile
     önce `sunucu.html` dosyasını sunar ("Directory listing for /sunucu/" hatasını önler).
  2. Inertia.js (`X-Inertia`), Next.js ve SPA yönlendirmelerini yakalayıp
     yerel `.html` sayfalarına tam sayfa geçişi yaptırır.
  3. Alt sayfalardan gelen göreceli varlık isteklerini (`/sunucu/img/x.png` -> `/img/x.png`)
     otomatik olarak kök klasörden tamamlar.
"""
from __future__ import annotations

import functools
import http.server
import mimetypes
import posixpath
import threading
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .paths import _with_query_hash

NAV_FIX_SCRIPT = b"""<script data-webclone-nav>
(function(){
  window.addEventListener('click', function(e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || a.target === '_blank' || a.hasAttribute('download')) return;
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^(javascript:|mailto:|tel:|data:)/i.test(href)) return;
    try {
      var u = new URL(href, window.location.href);
      if (u.origin === window.location.origin) {
        e.stopImmediatePropagation();
      }
    } catch (_) {}
  }, true);
})();
</script>"""


class SmartHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Klonlanmış siteleri kusursuz sunan HTTP işleyicisi."""

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

    def _root(self) -> Path:
        return Path(self.directory).resolve()

    def _resolve_target(self) -> tuple[Path | None, str | None]:
        """(dosya_yolu, yönlendirilecek_url) döndürür."""
        root = self._root()
        parts = urlsplit(self.path)
        raw_path = unquote(parts.path or "/")
        clean = posixpath.normpath(raw_path).lstrip("/")
        if clean in ("", "."):
            idx = root / "index.html"
            return (idx if idx.is_file() else None), None

        # Güvenlik: kök dışına çıkılmasın
        try:
            (root / clean).resolve().relative_to(root)
        except ValueError:
            return None, None

        # 1. Sorgu hash'li dosya eşleşmesi (?ver=1.2 vb.)
        if parts.query:
            q_cand = root / _with_query_hash(clean, parts.query)
            if q_cand.is_file():
                return q_cand, None

        # 2. Tam dosya eşleşmesi (örn. style.css, sunucu.html)
        exact = root / clean
        if exact.is_file():
            return exact, None

        # 3. .html uzantılı sayfa eşleşmesi (klasör çakışmasından ÖNCE bakılır!)
        # Örn: hem `sunucu.html` hem `sunucu/` klasörü varsa `/sunucu` -> `sunucu.html`
        html_cand = root / f"{clean}.html"
        if html_cand.is_file():
            if raw_path.endswith("/"):
                # Göreceli yolların bozulmaması için /sunucu/ -> /sunucu.html yönlendir
                return None, f"/{clean}.html"
            return html_cand, None

        # 4. Klasör içi index.html eşleşmesi (örn. /blog/ -> blog/index.html)
        idx_cand = root / clean / "index.html"
        if idx_cand.is_file():
            if not raw_path.endswith("/"):
                return None, f"/{clean}/"
            return idx_cand, None

        # 5. Alt sayfalardan bozuk göreceli varlık isteği (örn. /sunucu/img/a.png -> /img/a.png)
        segs = clean.split("/")
        for i in range(1, len(segs)):
            sub = "/".join(segs[i:])
            sub_cand = root / sub
            if sub_cand.is_file():
                return sub_cand, None
            sub_html = root / f"{sub}.html"
            if sub_html.is_file():
                return sub_html, None

        # 6. Hash'lenmiş varlık yedeği (style.css istendi ama style_8d2e83e6.css var)
        parent = exact.parent
        if parent.is_dir() and exact.suffix:
            matches = list(parent.glob(f"{exact.stem}_*{exact.suffix}"))
            if matches and matches[0].is_file():
                return matches[0], None

        return None, None

    def _serve_Request(self, send_body: bool) -> None:
        # Inertia.js XHR isteği geldiyse tam sayfa yüklemeye zorla (beyaz modal hatasını önler)
        if self.headers.get("X-Inertia"):
            target_file, redirect_url = self._resolve_target()
            loc = redirect_url or self.path
            if target_file:
                rel = target_file.relative_to(self._root()).as_posix()
                loc = "/" if rel == "index.html" else f"/{rel}"
            self.send_response(409, "Conflict")
            self.send_header("X-Inertia-Location", loc)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        target_file, redirect_url = self._resolve_target()
        if redirect_url:
            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if not target_file or not target_file.is_file():
            self.send_error(404, "Dosya bulunamadi")
            return

        try:
            data = target_file.read_bytes()
        except OSError:
            self.send_error(500, "Dosya okunamadi")
            return

        ctype = mimetypes.guess_type(target_file.name)[0] or "application/octet-stream"
        if target_file.suffix.lower() in (".html", ".htm"):
            ctype = "text/html; charset=utf-8"
            if b"data-webclone-nav" not in data:
                if b"</head>" in data:
                    data = data.replace(b"</head>", NAV_FIX_SCRIPT + b"</head>", 1)
                else:
                    data = NAV_FIX_SCRIPT + data

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if send_body:
            self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        self._serve_Request(send_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve_Request(send_body=False)


def create_server(directory: str | Path, port: int = 0) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(SmartHTTPRequestHandler, directory=str(directory))
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)


class PreviewServer:
    """GUI için arka planda çalışan yerel HTTP önizleme sunucusu."""

    def __init__(self) -> None:
        self._server: http.server.ThreadingHTTPServer | None = None
        self._dir: Path | None = None
        self.port: int = 0

    def serve(self, directory: Path) -> str:
        directory = directory.resolve()
        if self._server and self._dir == directory:
            return f"http://127.0.0.1:{self.port}"
        self.stop()
        self._server = create_server(directory, port=0)
        self.port = self._server.server_address[1]
        self._dir = directory
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.port}"

    def stop(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:  # noqa: BLE001
                pass
            self._server = None
            self._dir = None
