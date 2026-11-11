"""Gelişmiş sayfa ve varlık indirme katmanı (curl HTTP/2 + Chromium WebEngine).

Windows ve Linux çapraz platform uyumluluğu:
  - Windows konsol penceresi açılmasını engelleyen CREATE_NO_WINDOW bayrağı
  - Proxy (HTTP/HTTPS/SOCKS5) desteğinin curl ve Chromium'a aktarılması
  - Güçlendirilmiş hata yakalama ve geri dönüş (fallback) mekanizması
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

CURL_BIN = shutil.which("curl")
_META_MARKER = b"\n__WEBCLONE_META__:"

DEFAULT_FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"

# Windows'ta alt süreçlerin konsol penceresi açmasını engelle
_SUBPROCESS_KWARGS: dict = {}
if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000
    _SUBPROCESS_KWARGS["creationflags"] = CREATE_NO_WINDOW


@dataclass
class FetchResponse:
    url: str
    status_code: int
    content: bytes
    content_type: str

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": self.content_type}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def fetch_via_curl(
    url: str,
    referer: str | None = None,
    timeout: float = 15.0,
    user_agent: str | None = None,
    proxy: str | None = None,
) -> FetchResponse:
    """curl üzerinden HTTP/2 + Brotli/gzip/zstd ile indirir."""
    if not CURL_BIN:
        raise RuntimeError("Sistemde curl bulunamadi")

    attempts = [
        (["--http2"], user_agent or DEFAULT_FIREFOX_UA),
        (["--http1.1"], "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
    ]
    last_err = "curl bağlantı hatası"

    for proto_flags, ua in attempts:
        cmd = [
            CURL_BIN,
            "-4",
            "-sS",
            "-L",
            "-k",
            *proto_flags,
            "--compressed",
            "--connect-timeout", "6",
            "--max-time", str(max(6, int(timeout))),
            "-A", ua,
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "-H", "Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "-H", "Upgrade-Insecure-Requests: 1",
        ]
        if proxy:
            cmd.extend(["--proxy", proxy])
        if referer:
            cmd.extend(["-e", referer])
        cmd.extend([
            "-o", "-",
            "-w", "\n__WEBCLONE_META__:%{http_code}|%{url_effective}|%{content_type}",
            url,
        ])

        try:
            proc = subprocess.run(cmd, capture_output=True, check=False, **_SUBPROCESS_KWARGS)
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            continue

        raw = proc.stdout
        if _META_MARKER in raw:
            body, _, meta_bytes = raw.rpartition(_META_MARKER)
            parts = meta_bytes.decode("utf-8", "replace").strip().split("|", 2)
            code = int(parts[0]) if parts and parts[0].isdigit() else 0
            final_url = parts[1] if len(parts) > 1 and parts[1] else url
            ctype = parts[2] if len(parts) > 2 else ""
            if 200 <= code < 400 and body:
                return FetchResponse(url=final_url, status_code=code, content=body, content_type=ctype)
            if code >= 400:
                last_err = f"HTTP {code}"
        else:
            err_txt = proc.stderr.decode("utf-8", "replace").strip()
            last_err = err_txt or f"curl çıkış kodu: {proc.returncode}"

    raise RuntimeError(last_err)


def fetch_via_chromium(
    url: str,
    timeout: float = 25.0,
    proxy: str | None = None,
) -> FetchResponse:
    """PyQt6-WebEngine (gerçek Chromium) alt süreciyle sayfayı render edip HTML'ini döndürür."""
    cmd = [sys.executable, "-m", "webclone.browser", url, str(int(timeout))]
    if proxy:
        cmd.append(proxy)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
            check=False,
            **_SUBPROCESS_KWARGS,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Chromium zaman aşımına uğradı")

    out = proc.stdout
    marker = "__WEBCLONE_CHROMIUM_JSON__:"
    if marker not in out:
        err = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "Chromium başlatılamadı"
        raise RuntimeError(err)
    payload = json.loads(out.split(marker, 1)[1].strip())
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    html_bytes = payload["html"].encode("utf-8", "surrogateescape")
    return FetchResponse(
        url=payload.get("url") or url,
        status_code=200,
        content=html_bytes,
        content_type="text/html; charset=utf-8",
    )


def _chromium_worker_main(url: str, timeout_sec: int, proxy: str | None = None) -> int:
    """Alt süreçte çalışan görünmez Chromium (QWebEnginePage) betiği."""
    try:
        from PyQt6.QtCore import QTimer, QUrl
        from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
        from PyQt6.QtWidgets import QApplication
    except Exception as e:  # noqa: BLE001
        print("__WEBCLONE_CHROMIUM_JSON__:" + json.dumps({"error": f"PyQt6-WebEngine kütüphanesi yok: {e}"}))
        return 1

    app_args = list(sys.argv)
    if proxy:
        app_args.append(f"--proxy-server={proxy}")

    app = QApplication(app_args)
    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    class _SilentPage(QWebEnginePage):
        def javaScriptConsoleMessage(self, *args):  # noqa: N802
            pass

    page = _SilentPage(profile)
    settings = page.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    if hasattr(page, "certificateError"):
        page.certificateError.connect(lambda err: err.acceptCertificate())

    state = {"done": False}

    def emit_result(html: str = "", error: str = "") -> None:
        if state["done"]:
            return
        state["done"] = True
        data = {"url": page.url().toString() or url, "html": html, "error": error}
        print("__WEBCLONE_CHROMIUM_JSON__:" + json.dumps(data, ensure_ascii=False), flush=True)
        app.quit()

    def grab_html() -> None:
        page.toHtml(lambda html: emit_result(html=html))

    def on_loaded(ok: bool) -> None:
        # Sayfayı aşağı kaydırıp lazy-load görselleri tetikle
        page.runJavaScript(
            """
            (function(){
              try {
                window.scrollTo(0, document.body.scrollHeight / 2);
                setTimeout(function(){ window.scrollTo(0, document.body.scrollHeight); }, 300);
                setTimeout(function(){ window.scrollTo(0, 0); }, 600);
              } catch(e) {}
            })();
            """
        )
        QTimer.singleShot(1200, grab_html)

    page.loadFinished.connect(on_loaded)
    QTimer.singleShot(timeout_sec * 1000, grab_html)
    page.load(QUrl(url))
    return app.exec()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else ""
    t_sec = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    px = sys.argv[3] if len(sys.argv) > 3 else None
    sys.exit(_chromium_worker_main(target, t_sec, px))
