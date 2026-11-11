"""Uçtan uca test: yerel sahte bir siteyi ayağa kaldırır, klonlar, sonucu doğrular.

Çalıştırma:  python -m unittest discover -s tests -v
"""
import functools
import http.server
import re
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from webclone import CloneOptions, Cloner  # noqa: E402
from webclone.rewrite import parse_srcset  # noqa: E402

PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
       b"\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00"
       b"\x00\x00\x00IEND\xaeB`\x82")

SITE = {
    "index.html": """<!DOCTYPE html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">
<title>Test Şirketi</title>
<link rel="stylesheet" href="/css/style.css?ver=1.2" integrity="sha384-xxx" crossorigin="anonymous">
<link rel="icon" href="favicon.png">
<link rel="canonical" href="/">
<style>.hero{background:url('img/hero.png')}</style>
</head><body background="img/bg.png">
<svg viewBox="0 0 10 10"><use href="img/sprite.svg#ikon"></use></svg>
<img src="img/logo.png" srcset="img/logo.png 1x, img/logo@2x.png 2x" alt="Logo &amp; marka">
<img data-src="img/lazy.png" alt="lazy">
<div style="background-image: url(&quot;img/div.png&quot;)">Merhaba dünya</div>
<a href="/hakkinda">Hakkında</a> <a href="blog/">Blog</a> <a href="#ust">Üst</a>
<a href="https://example.org/dis">Dış link</a> <a href="mailto:a@b.c">Mail</a>
<script src="js/app.js"></script>
<script>var x = "<div>" && 1 < 2;</script>
</body></html>""",
    "hakkinda.html": """<html><head><link rel="stylesheet" href="css/style.css?ver=1.2"></head>
<body><img src="/img/logo.png"><a href="/">Ana sayfa</a><a href="/derin">Derin</a></body></html>""",
    "blog/index.html": """<html><head><base href="/blog/"><link rel="stylesheet" href="../css/style.css?ver=1.2"></head>
<body><img src="resim.png"></body></html>""",
    "blog/resim.png": PNG,
    "css/style.css": """@import url("reset.css");
@import "theme.css";
@font-face{font-family:X;src:url(../fonts/x.woff2) format("woff2"),url('../fonts/x.woff') format("woff")}
body{background:url(../img/bg.png)} .i{background:url(data:image/png;base64,AAAA)}""",
    "css/reset.css": "*{margin:0}",
    "css/theme.css": ".t{background:url('/img/theme.png')}",
    "js/app.js": "console.log('merhaba');",
    "fonts/x.woff2": b"wOF2fake",
    "fonts/x.woff": b"wOFFfake",
    "favicon.png": PNG,
    "img/sprite.svg": '<svg xmlns="http://www.w3.org/2000/svg"><symbol id="ikon"/></svg>',
}
for name in ["hero", "bg", "logo", "logo@2x", "lazy", "div", "theme"]:
    SITE[f"img/{name}.png"] = PNG


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        # /hakkinda -> hakkinda.html (temiz URL desteği)
        path = self.translate_path(self.path)
        if not Path(path).exists() and Path(path + ".html").exists():
            self.path = self.path.split("?")[0] + ".html"
        return super().send_head()


class CloneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name) / "site"
        for name, content in SITE.items():
            f = root / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        handler = functools.partial(_Handler, directory=str(root))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.tmp.cleanup()

    def clone(self, **kw):
        out = Path(self.tmp.name) / f"out_{kw.get('layout', 'organized')}_{kw.get('depth', 0)}"
        events = []
        res = Cloner(self.base, out, CloneOptions(**kw), on_event=lambda n, d: events.append(n)).run()
        return res, out, events

    def assert_all_local_refs_exist(self, out: Path):
        """Çıktıdaki tüm göreceli src/href/url() referansları gerçekten var olan dosyalara gitmeli."""
        for f in out.rglob("*"):
            if f.suffix not in (".html", ".css"):
                continue
            text = f.read_text("utf-8")
            refs = re.findall(r'(?:src|href|background)="([^"]+)"', text)
            refs += re.findall(r'url\("([^"]+)"\)', text)
            for srcset in re.findall(r'srcset="([^"]+)"', text):
                refs += [u for u, _ in parse_srcset(srcset)]
            for ref in refs:
                if ref.startswith(("http", "#", "mailto:", "data:")):
                    continue
                target = (f.parent / ref.split("#")[0]).resolve()
                self.assertTrue(target.exists(), f"{f.relative_to(out)} -> {ref} bulunamadı")

    def test_single_page_organized(self):
        res, out, events = self.clone(depth=0)
        self.assertFalse(res.failed, res.failed)
        self.assertEqual(res.pages, ["index.html"])
        html = (out / "index.html").read_text("utf-8")

        self.assertIn('href="assets/css/style_', html)           # ?ver= hash'li ad
        self.assertNotIn("integrity", html)                       # SRI kaldırıldı
        self.assertNotIn("Content-Security-Policy", html)         # CSP kaldırıldı
        self.assertIn('viewBox="0 0 10 10"', html)                # SVG büyük harfi korundu
        self.assertIn("assets/img/sprite.svg#ikon", html)         # fragment korundu
        self.assertIn("assets/img/logo@2x.png 2x", html)          # srcset
        self.assertIn('data-src="assets/img/lazy.png"', html)     # lazy-load
        self.assertIn("url(\"assets/img/hero.png\")", html)       # <style>
        self.assertIn("url(&quot;assets/img/div.png&quot;)", html)  # style=""
        self.assertIn(f'href="{self.base}hakkinda"', html)        # depth=0 -> mutlak link
        self.assertIn('href="#ust"', html)
        self.assertIn('var x = "<div>" && 1 < 2;', html)          # inline JS dokunulmadı
        self.assertIn("Test Şirketi", html)
        self.assertIn("Logo &amp; marka", html)

        css = next((out / "assets/css").glob("style_*.css")).read_text("utf-8")
        self.assertIn('url("../fonts/x.woff2")', css)
        self.assertIn('@import url("reset.css")', css)
        self.assertIn("data:image/png;base64,AAAA", css)
        self.assertTrue((out / "assets/img/theme.png").exists())  # @import içindeki CSS'in görseli
        self.assertTrue((out / "assets/js/app.js").exists())
        self.assertIn("finished", events)
        self.assert_all_local_refs_exist(out)

    def test_crawl_depth_1(self):
        res, out, _ = self.clone(depth=1)
        self.assertFalse(res.failed, res.failed)
        self.assertEqual(sorted(res.pages), ["blog/index.html", "hakkinda.html", "index.html"])
        index = (out / "index.html").read_text("utf-8")
        self.assertIn('href="hakkinda.html"', index)
        self.assertIn('href="blog/index.html"', index)
        about = (out / "hakkinda.html").read_text("utf-8")
        self.assertIn('href="index.html"', about)                 # geri link yerel
        self.assertIn(f'href="{self.base}derin"', about)          # derinlik dışı -> mutlak
        blog = (out / "blog/index.html").read_text("utf-8")
        self.assertNotIn("<base", blog)
        self.assertIn('href="../assets/css/style_', blog)
        self.assertTrue((out / "assets/img/resim.png").exists())
        self.assert_all_local_refs_exist(out)

    def test_mirror_layout(self):
        res, out, _ = self.clone(depth=0, layout="mirror")
        self.assertFalse(res.failed, res.failed)
        self.assertTrue((out / "img/logo.png").exists())
        self.assertTrue((out / "fonts/x.woff2").exists())
        self.assertTrue(list((out / "css").glob("style_*.css")))
        self.assert_all_local_refs_exist(out)

    def test_bad_url(self):
        res = Cloner(self.base + "yok-boyle-sayfa", Path(self.tmp.name) / "bad").run()
        self.assertEqual(res.pages, [])
        self.assertTrue(res.failed)

    def test_windows_reserved_names(self):
        from webclone.paths import safe_segment
        self.assertEqual(safe_segment("con.html"), "_con.html")
        self.assertEqual(safe_segment("aux.png"), "_aux.png")
        self.assertEqual(safe_segment("nul"), "_nul")
        self.assertEqual(safe_segment("com1.txt"), "_com1.txt")
        self.assertFalse(safe_segment("normal_file.js").startswith("_normal"))

    def test_stealth_headers(self):
        from webclone.stealth import StealthManager
        sm = StealthManager(profile_name="Chrome (Windows 11)", referer_mode="google")
        headers = sm.get_headers("https://example.com/", is_page=True)
        self.assertIn("User-Agent", headers)
        self.assertIn("Windows", headers["User-Agent"])
        self.assertEqual(headers["Referer"], "https://www.google.com/")
        self.assertEqual(headers["DNT"], "1")
        self.assertEqual(headers["Sec-GPC"], "1")
        self.assertEqual(headers["sec-ch-ua-platform"], '"Windows"')

    def test_recon_collection(self):
        from webclone.recon import ReconCollector
        recon = ReconCollector("http://127.0.0.1:8000/")
        recon.analyze_response({
            "Server": "nginx/1.24.0",
            "X-Powered-By": "Next.js",
            "Strict-Transport-Security": "max-age=31536000",
        }, status_code=200)
        recon.analyze_html("""
            <html><head><title>Harika Site</title><meta name="description" content="Test aciklama">
            <meta property="og:title" content="OG Baslik">
            </head><body><div id="__NEXT_DATA__"></div></body></html>
        """)
        self.assertEqual(recon.report.server, "nginx/1.24.0")
        self.assertEqual(recon.report.meta_title, "Harika Site")
        self.assertEqual(recon.report.og_data.get("title"), "OG Baslik")
        tech_names = [t["name"] for t in recon.report.technologies]
        self.assertIn("Next.js", tech_names)
        self.assertIn("Nginx", tech_names)
        
        # HTML raporu üretimi kontrolü
        html_report = recon.render_html_report()
        self.assertIn("Harika Site", html_report)
        self.assertIn("Hedef İstihbarat", html_report)


if __name__ == "__main__":
    unittest.main()
