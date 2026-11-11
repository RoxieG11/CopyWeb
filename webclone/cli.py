"""Komut satırı arayüzü:  python -m webclone https://site.com"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import threading

from .core import CloneOptions, Cloner
from .server import create_server
from .stealth import PROFILES


def _setup_windows_console() -> None:
    """Windows CMD konsolunda ANSI renklerini ve UTF-8 çıkışını etkinleştirir."""
    if sys.platform == "win32":
        try:
            os.system("")  # VT100 modunu aktif eder
            if sys.stdout.encoding.lower() != "utf-8":
                sys.stdout.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="webclone",
        description="WebClone v2.0 — Web sitelerinin HTML, CSS, JS, görsel, font ve verilerini tam yerel kopyalar.",
    )
    p.add_argument("url", nargs="?", help="Kopyalanacak sayfanın adresi (boş bırakılırsa GUI açılır)")
    p.add_argument("-g", "--gui", action="store_true", help="Masaüstü arayüzünü (GUI) başlat")
    p.add_argument("-o", "--output", help="Çıktı klasörü (varsayılan: output/<alan-adı>)")
    p.add_argument("-d", "--depth", type=int, default=0,
                   help="Link takip derinliği. 0=sadece bu sayfa, 1=+linklediği sayfalar (varsayılan: 0)")
    p.add_argument("--max-pages", type=int, default=50, help="En fazla indirilecek sayfa (varsayılan: 50)")
    p.add_argument("-w", "--workers", type=int, default=16, help="Eşzamanlı iş parçacığı sayısı (varsayılan: 16)")
    p.add_argument("--timeout", type=float, default=12, help="İstek zaman aşımı, saniye (varsayılan: 12)")
    p.add_argument("--layout", choices=["organized", "mirror"], default="organized",
                   help="organized: assets/css, assets/img... | mirror: sunucudaki yol yapısı")
    p.add_argument("--no-external", action="store_true",
                   help="Başka alan adlarındaki (CDN vb.) dosyaları indirme, linkini bırak")
    p.add_argument("--render-js", action="store_true",
                   help="Sayfaları gerçek Chromium (WebEngine) ile açıp JS çalıştıktan sonra kopyala")
    p.add_argument("--strict-ssl", action="store_true", help="Sıkı SSL sertifika doğrulamasını zorunlu tut")
    p.add_argument("--zip", action="store_true", help="Bitince klasörü .zip olarak da paketle")
    p.add_argument("--serve", nargs="?", const=8000, type=int, metavar="PORT",
                   help="Bitince sonucu yerel sunucuda yayınla (varsayılan port: 8000)")

    # Gizlilik & Anonimlik
    stealth_group = p.add_argument_group("Gizlilik & Anonimlik Seçenekleri")
    stealth_group.add_argument("--proxy", help="Vekil sunucu adresi (örn: http://ip:port veya socks5://127.0.0.1:9050)")
    stealth_group.add_argument("--ua", default="random",
                               help="User-Agent profili ('random', 'Chrome (Windows 11)', 'Firefox (Linux)' vb.)")
    stealth_group.add_argument("--rotate-ua", action="store_true", help="Her istekte farklı bir User-Agent kullan")
    stealth_group.add_argument("--referer", default="google", help="Referer modu (google, duckduckgo, bing, self, none)")
    stealth_group.add_argument("--delay", type=float, default=0.0, help="İstekler arası insan gecikmesi / jitter (saniye)")

    # İstihbarat & Bilgi Toplama
    recon_group = p.add_argument_group("İstihbarat & Bilgi Toplama")
    recon_group.add_argument("--no-recon", action="store_true", help="Hedef istihbarat raporunu (robots/sitemap/tech) kapat")

    p.add_argument("-q", "--quiet", action="store_true", help="Sadece özet yazdır")
    p.add_argument("-v", "--verbose", action="store_true", help="Her dosyayı ayrı satırda yazdır")
    return p


class ConsoleReporter:
    def __init__(self, quiet: bool, verbose: bool):
        self.quiet = quiet
        self.verbose = verbose
        self.tty = sys.stdout.isatty()
        self._lock = threading.Lock()

    def _line(self, text: str) -> None:
        with self._lock:
            if self.tty:
                sys.stdout.write("\r\033[K")
            print(text, flush=True)

    def _status(self, text: str) -> None:
        if self.tty and not self.verbose:
            with self._lock:
                term_w = shutil.get_terminal_size((80, 20)).columns
                sys.stdout.write("\r\033[K" + text[: term_w - 1])
                sys.stdout.flush()

    def __call__(self, name: str, data: dict) -> None:
        if self.quiet:
            return
        if name == "start":
            self._line(f"🚀 Klonlama Başlatıldı: {data['url']}\n📁 Hedef Klasör: {data['output_dir']}")
        elif name == "recon_done":
            rep = data.get("report")
            if rep:
                tech_list = ", ".join(t["name"] for t in rep.technologies[:5]) or "Tespit edilemedi"
                self._line(f"🔍 İstihbarat: IP={rep.ip_address} | Sunucu={rep.server} | Teknolojiler: {tech_list}")
        elif name == "page_start":
            self._line(f"📄 [SAYFA] {data['url']}  →  {data['path']}")
        elif name == "page_failed":
            self._line(f"❌ [HATA] Sayfa {data['url']}: {data['error']}")
        elif name == "asset_done":
            size_kb = data.get("size", 0) / 1024
            msg = f"  ✓ [{data['done']}/{data['total']}] {data['kind'].upper():5} {data['path']} ({size_kb:.1f} KB)"
            if self.verbose:
                self._line(msg)
            else:
                self._status(msg)
        elif name == "asset_failed":
            self._line(f"  ⚠ [HATA] {data['url']}: {data['error']}")


def main(argv: list[str] | None = None) -> int:
    _setup_windows_console()
    args = build_parser().parse_args(argv)
    if args.gui or not args.url:
        from .gui import launch_gui
        return launch_gui(initial_url=args.url or "")

    opts = CloneOptions(
        depth=max(0, args.depth),
        max_pages=args.max_pages,
        workers=max(1, args.workers),
        timeout=args.timeout,
        layout=args.layout,
        external_assets=not args.no_external,
        verify_ssl=bool(args.strict_ssl),
        render_js=bool(args.render_js),
        user_agent_profile=args.ua,
        rotate_ua=bool(args.rotate_ua),
        proxy=args.proxy,
        referer_mode=args.referer,
        min_delay=args.delay,
        max_delay=args.delay * 1.5 if args.delay > 0 else 0.0,
        collect_recon=not args.no_recon,
    )

    cancel = threading.Event()
    cloner = Cloner(args.url, args.output, opts, ConsoleReporter(args.quiet, args.verbose), cancel)
    try:
        result = cloner.run()
    except KeyboardInterrupt:
        cancel.set()
        print("\n⏹ İptal edildi.")
        return 130

    print()
    print("=" * 65)
    if not result.pages:
        print("❌ Klonlama başarısız oldu: Ana sayfa indirilemedi.")
        for url, err in result.failed:
            print(f"  • {url}: {err}")
        return 1

    total_mb = result.total_bytes / (1024 * 1024)
    print(f"✅ KLONLAMA TAMAMLANDI ({result.elapsed:.1f} sn | {total_mb:.2f} MB)")
    print(f"  • Sayfa sayısı : {len(result.pages)}")
    print(f"  • Dosya sayısı : {result.assets_ok}")
    print(f"  • Hatalı       : {len(result.failed)}")
    print(f"  • Klasör       : {result.output_dir.resolve()}")
    if result.index_file:
        print(f"  • Ana Dosya    : {result.index_file.resolve()}")
    if result.recon_html:
        print(f"  • Rapor (HTML) : {result.recon_html.resolve()}")

    if args.zip:
        archive = shutil.make_archive(str(result.output_dir), "zip", result.output_dir)
        print(f"  • ZIP Arşivi   : {archive}")

    if args.serve and result.index_file:
        rel = result.index_file.relative_to(result.output_dir).as_posix()
        with create_server(result.output_dir, port=args.serve) as srv:
            print(f"\n🌐 Canlı Yayında: http://127.0.0.1:{args.serve}/{rel}  (Durdurmak için Ctrl+C)")
            try:
                srv.serve_forever()
            except KeyboardInterrupt:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
