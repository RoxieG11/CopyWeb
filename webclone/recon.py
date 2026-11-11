"""WebClone Hedef Bilgi Toplama ve İstihbarat (Reconnaissance) Modülü.

Hedef web sitesi hakkında kapsamlı bilgi toplar:
  - DNS, IP ve Sunucu Bilgileri
  - HTTP Yanıt Başlıkları & Güvenlik Değerlendirmesi (HSTS, CSP vb.)
  - Teknoloji Yığını Tespiti (CMS, Framework, Kütüphaneler, CSS Motorları, Analitik)
  - robots.txt ve sitemap.xml Keşfi
  - SEO ve OpenGraph / Sosyal Medya Meta Verileri
  - Bağımsız, şık HTML ve JSON Raporu Üretimi
"""
from __future__ import annotations

import html
import json
import re
import socket
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

# Teknoloji imzaları: (Ad, Kategori, regex_veya_aranacak_kelimeler)
TECH_SIGNATURES: list[tuple[str, str, list[str]]] = [
    # CMS / Platformlar
    ("WordPress", "CMS", ["wp-content", "wp-includes", 'generator" content="wordpress']),
    ("Shopify", "E-Ticaret", ["cdn.shopify.com", "shopify.theme", "myshopify.com"]),
    ("WooCommerce", "E-Ticaret", ["woocommerce", "wc-ajax"]),
    ("Webflow", "Web Tasarım", ["assets.website-files.com", "webflow.js", "w-nav"]),
    ("Wix", "Web Tasarım", ["wix.com", "_wix_", "wixstatic.com"]),
    ("Squarespace", "Web Tasarım", ["squarespace.com", "static1.squarespace.com"]),
    ("Drupal", "CMS", ["drupal.settings", "drupal.js", 'generator" content="drupal']),
    ("Ghost", "Blog/CMS", ["ghost.org", 'generator" content="ghost']),
    ("Joomla", "CMS", ["joomla!", 'generator" content="joomla']),
    ("Magento", "E-Ticaret", ["mage/cookies.js", "skin/frontend", "varien"]),
    # Frontend Çatıları
    ("Next.js", "Frontend Framework", ["__NEXT_DATA__", "/_next/static/"]),
    ("Nuxt.js", "Frontend Framework", ["__NUXT__", "/_nuxt/"]),
    ("React", "JavaScript Kütüphanesi", ["react", "react-dom", "_reactRootContainer"]),
    ("Vue.js", "JavaScript Framework", ["vue.min.js", "vue.global", "data-v-"]),
    ("Angular", "JavaScript Framework", ["ng-version", "ng-app", "angular.min.js"]),
    ("Svelte", "JavaScript Framework", ["svelte-", "__svelte"]),
    ("Inertia.js", "SPA Köprüsü", ["data-page=", "x-inertia"]),
    ("Astro", "Web Framework", ["data-astro-", "astro-island"]),
    # CSS Çatıları
    ("Tailwind CSS", "CSS Framework", ["tailwindcss", "tailwind", "text-slate-", "bg-slate-", "dark:"]),
    ("Bootstrap", "CSS Framework", ["bootstrap.min.css", "bootstrap.bundle", "btn-primary"]),
    ("Bulma", "CSS Framework", ["bulma.min.css", "is-primary"]),
    # JS Kütüphaneleri
    ("jQuery", "JavaScript Kütüphanesi", ["jquery.min.js", "jquery.js", "jquery-"]),
    ("Swiper", "Slider Kütüphanesi", ["swiper-bundle", "swiper.min.js"]),
    ("FontAwesome", "İkon Paketi", ["font-awesome", "fontawesome", "fa-solid", "fa-brands"]),
    ("GSAP", "Animasyon", ["gsap.min.js", "tweenmax"]),
    ("Three.js", "3D Görselleştirme", ["three.min.js", "three.module.js"]),
    ("Alpine.js", "JavaScript Framework", ["alpine.min.js", "x-data", "x-show"]),
    ("HTMX", "Kütüphane", ["htmx.org", "hx-get", "hx-post"]),
    # Analitik ve Pazarlama
    ("Google Analytics 4", "Analitik", ["googletagmanager.com/gtag/js", "gtag("]),
    ("Google Tag Manager", "Etiket Yöneticisi", ["googletagmanager.com/gtm.js"]),
    ("Facebook Pixel", "Reklam Takibi", ["fbevents.js", "fbq("]),
    ("Hotjar", "Kullanıcı Takibi", ["static.hotjar.com"]),
    ("Cloudflare Turnstile", "Güvenlik / Captcha", ["challenges.cloudflare.com/turnstile"]),
    ("Google reCAPTCHA", "Güvenlik / Captcha", ["google.com/recaptcha/api.js"]),
]

SECURITY_HEADERS = [
    ("Strict-Transport-Security", "HSTS", "HTTPS zorunluluğu sağlar"),
    ("Content-Security-Policy", "CSP", "XSS ve kod enjeksiyonunu engeller"),
    ("X-Frame-Options", "Clickjacking Koruması", "Sayfanın iframe içine alınmasını engeller"),
    ("X-Content-Type-Options", "MIME Sniffing Koruması", "MIME türü karışıklığı saldırılarını önler"),
    ("Referrer-Policy", "Referrer Gizliliği", "Referer başlığının dışarı sızmasını kısıtlar"),
    ("Permissions-Policy", "İzin Politikası", "Tarayıcı özelliklerine (kamera, konum vb.) erişimi sınırlar"),
]


@dataclass
class ReconReport:
    target_url: str
    hostname: str
    ip_address: str = ""
    server: str = ""
    powered_by: str = ""
    status_code: int = 0
    technologies: list[dict[str, str]] = field(default_factory=list)
    security_headers: list[dict[str, Any]] = field(default_factory=list)
    raw_headers: dict[str, str] = field(default_factory=dict)
    meta_title: str = ""
    meta_description: str = ""
    meta_keywords: str = ""
    og_data: dict[str, str] = field(default_factory=dict)
    twitter_data: dict[str, str] = field(default_factory=dict)
    language: str = ""
    robots_found: bool = False
    robots_sitemaps: list[str] = field(default_factory=list)
    robots_disallow: list[str] = field(default_factory=list)
    discovered_sitemap_urls: list[str] = field(default_factory=list)
    asset_breakdown: dict[str, int] = field(default_factory=dict)
    total_size_bytes: int = 0


class ReconCollector:
    """Hedef web sitesinin tüm istihbaratını toplayan motor."""

    def __init__(self, target_url: str, session: Any = None):
        self.target_url = target_url
        parts = urlsplit(target_url)
        self.hostname = parts.hostname or ""
        self.base_origin = f"{parts.scheme}://{parts.netloc}"
        self.session = session
        self.report = ReconReport(target_url=target_url, hostname=self.hostname)

    def resolve_dns(self) -> None:
        """Hedefin IP adresini bulur."""
        if not self.hostname:
            return
        try:
            ip = socket.gethostbyname(self.hostname)
            self.report.ip_address = ip
        except Exception:  # noqa: BLE001
            self.report.ip_address = "Çözümlenemedi"

    def analyze_response(self, headers: dict[str, str], status_code: int = 200) -> None:
        """HTTP yanıt başlıklarını analiz eder ve güvenlik değerlendirmesi yapar."""
        self.report.status_code = status_code
        self.report.raw_headers = dict(headers)
        self.report.server = headers.get("Server", headers.get("server", "Bilinmiyor"))
        self.report.powered_by = headers.get("X-Powered-By", headers.get("x-powered-by", ""))

        # Güvenlik başlıklarını kontrol et
        sec_results = []
        lower_headers = {k.lower(): v for k, v in headers.items()}
        for h_name, title, desc in SECURITY_HEADERS:
            present = h_name.lower() in lower_headers
            val = lower_headers.get(h_name.lower(), "")
            sec_results.append({
                "header": h_name,
                "title": title,
                "description": desc,
                "present": present,
                "value": val,
            })
        self.report.security_headers = sec_results

        # Sunucu başlığından teknoloji çıkar
        server_val = self.report.server.lower()
        if "cloudflare" in server_val:
            self._add_tech("Cloudflare", "CDN / Güvenlik")
        elif "nginx" in server_val:
            self._add_tech("Nginx", "Web Sunucusu")
        elif "apache" in server_val:
            self._add_tech("Apache", "Web Sunucusu")
        elif "litespeed" in server_val:
            self._add_tech("LiteSpeed", "Web Sunucusu")
        elif "caddy" in server_val:
            self._add_tech("Caddy", "Web Sunucusu")
        elif "microsoft-iis" in server_val:
            self._add_tech("Microsoft IIS", "Web Sunucusu")

        if self.report.powered_by:
            self._add_tech(self.report.powered_by, "Backend Platform")

    def _add_tech(self, name: str, category: str) -> None:
        for t in self.report.technologies:
            if t["name"].lower() == name.lower():
                return
        self.report.technologies.append({"name": name, "category": category})

    def analyze_html(self, html_text: str) -> None:
        """HTML kaynak kodunu tarar; teknolojileri, SEO ve sosyal medya meta verilerini çıkarır."""
        lower_html = html_text.lower()

        # Teknoloji tespiti
        for name, category, patterns in TECH_SIGNATURES:
            if any(p.lower() in lower_html for p in patterns):
                self._add_tech(name, category)

        # Meta Başlık (<title>)
        m_title = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        if m_title:
            self.report.meta_title = html.unescape(m_title.group(1).strip())

        # Dil (<html lang="...">)
        m_lang = re.search(r"<html[^>]+lang=[\"']?([a-zA-Z-]+)", html_text, re.IGNORECASE)
        if m_lang:
            self.report.language = m_lang.group(1).strip()

        # Meta Etiketleri Tara
        meta_tags = re.findall(r"<meta\s+([^>]+)>", html_text, re.IGNORECASE)
        for tag in meta_tags:
            name_m = re.search(r'(?:name|property)=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            content_m = re.search(r'content=["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if not name_m or not content_m:
                continue
            key = name_m.group(1).strip().lower()
            val = html.unescape(content_m.group(1).strip())

            if key == "description":
                self.report.meta_description = val
            elif key == "keywords":
                self.report.meta_keywords = val
            elif key.startswith("og:"):
                self.report.og_data[key[3:]] = val
            elif key.startswith("twitter:"):
                self.report.twitter_data[key[8:]] = val

    def fetch_robots_and_sitemaps(self) -> None:
        """robots.txt dosyasını çeker, kuralları ve sitemap adreslerini ayrıştırır."""
        if not self.session:
            return

        robots_url = urljoin(self.base_origin, "/robots.txt")
        try:
            r = self.session.get(robots_url, timeout=5)
            if r.status_code == 200 and r.text:
                self.report.robots_found = True
                for line in r.text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if ":" not in line:
                        continue
                    field_name, _, val = line.partition(":")
                    field_name = field_name.strip().lower()
                    val = val.strip()
                    if field_name == "sitemap":
                        if val not in self.report.robots_sitemaps:
                            self.report.robots_sitemaps.append(val)
                    elif field_name == "disallow" and val:
                        if val not in self.report.robots_disallow:
                            self.report.robots_disallow.append(val)
        except Exception:  # noqa: BLE001
            pass

        # Sitemap listesinden veya varsayılan sitemap.xml'den link topla
        sitemaps_to_try = list(self.report.robots_sitemaps)
        if not sitemaps_to_try:
            sitemaps_to_try.append(urljoin(self.base_origin, "/sitemap.xml"))

        discovered = []
        for sm_url in sitemaps_to_try[:3]:  # En fazla 3 sitemap incele
            try:
                r = self.session.get(sm_url, timeout=6)
                if r.status_code == 200 and r.content:
                    root = ET.fromstring(r.content)
                    # Namespace'leri temizle
                    for elem in root.iter():
                        if elem.tag.endswith("loc") and elem.text:
                            u = elem.text.strip()
                            if u.startswith("http") and u not in discovered:
                                discovered.append(u)
                                if len(discovered) >= 100:
                                    break
            except Exception:  # noqa: BLE001
                pass

        self.report.discovered_sitemap_urls = discovered

    def save_reports(self, output_dir: Path) -> tuple[Path, Path]:
        """`recon_report.json` ve `recon_report.html` dosyalarını belirtilen dizine kaydeder."""
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "recon_report.json"
        html_path = output_dir / "recon_report.html"

        # 1. JSON
        data = asdict(self.report)
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. HTML Raporu
        html_content = self.render_html_report()
        html_path.write_text(html_content, encoding="utf-8")

        return json_path, html_path

    def render_html_report(self) -> str:
        """Şık, modern ve bağımsız bir HTML İstihbarat Raporu oluşturur."""
        r = self.report
        tech_badges = "".join(
            f'<span class="badge badge-tech">{html.escape(t["name"])} <small>({html.escape(t["category"])})</small></span>'
            for t in r.technologies
        ) or '<span class="text-muted">Özel veya gizlenmiş altyapı</span>'

        sec_rows = ""
        for s in r.security_headers:
            status_icon = "✅" if s["present"] else "❌"
            badge_cls = "badge-success" if s["present"] else "badge-danger"
            val_text = html.escape(s["value"]) if s["present"] else "Eksik"
            sec_rows += f"""
            <tr>
              <td><strong>{html.escape(s["title"])}</strong><br><small class="text-muted">{html.escape(s["header"])}</small></td>
              <td><span class="badge {badge_cls}">{status_icon} {"Aktif" if s["present"] else "Eksik"}</span></td>
              <td class="code-cell">{val_text}</td>
              <td class="text-muted">{html.escape(s["description"])}</td>
            </tr>
            """

        og_rows = "".join(
            f"<tr><td><code>og:{html.escape(k)}</code></td><td>{html.escape(v)}</td></tr>"
            for k, v in r.og_data.items()
        ) or '<tr><td colspan="2" class="text-muted">OpenGraph etiketi bulunamadı</td></tr>'

        sitemap_items = "".join(
            f'<li><a href="{html.escape(u)}" target="_blank">{html.escape(u)}</a></li>'
            for u in r.discovered_sitemap_urls[:25]
        ) or '<li class="text-muted">Sitemap URL listesi bulunamadı veya korumalı</li>'

        robots_dis = "".join(
            f"<code>{html.escape(d)}</code> " for d in r.robots_disallow[:15]
        ) or '<span class="text-muted">Engellenen yol yok</span>'

        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hedef İstihbarat Raporu — {html.escape(r.hostname)}</title>
<style>
  :root {{
    --bg: #090d16;
    --surface: #111827;
    --card: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-glow: #0284c7;
    --success: #10b981;
    --danger: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    line-height: 1.5;
    padding: 30px 20px;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .header h1 {{ font-size: 24px; color: #fff; }}
  .header .url {{ color: var(--accent); font-family: monospace; font-size: 15px; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 24px; }}
  .card {{
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
  }}
  .card h2 {{
    font-size: 16px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
  }}
  .badge-tech {{
    background-color: rgba(56, 189, 248, 0.15);
    color: var(--accent);
    border: 1px solid rgba(56, 189, 248, 0.3);
    margin-right: 6px;
    margin-bottom: 6px;
  }}
  .badge-success {{ background-color: rgba(16, 185, 129, 0.2); color: #34d399; }}
  .badge-danger {{ background-color: rgba(239, 68, 68, 0.2); color: #f87171; }}
  .data-list {{ list-style: none; }}
  .data-list li {{
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }}
  .data-list li span:first-child {{ color: var(--muted); }}
  .table-responsive {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
  th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
  th {{ background-color: var(--card); color: var(--muted); font-weight: 600; }}
  .code-cell {{ font-family: monospace; font-size: 12px; max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .text-muted {{ color: var(--muted); }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  code {{ background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
  .sitemap-box {{ max-height: 220px; overflow-y: auto; padding: 10px; background: var(--bg); border-radius: 6px; }}
  .sitemap-box ul {{ padding-left: 20px; font-size: 13px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>🔍 Hedef İstihbarat & Güvenlik Raporu</h1>
      <div class="url">{html.escape(r.target_url)}</div>
    </div>
    <div>
      <span class="badge badge-tech" style="font-size:14px; padding:8px 14px;">IP: {html.escape(r.ip_address)}</span>
    </div>
  </div>

  <div class="grid">
    <!-- Sunucu & Altyapı -->
    <div class="card">
      <h2>🖥️ Sunucu & Altyapı</h2>
      <ul class="data-list">
        <li><span>Alan Adı:</span> <strong>{html.escape(r.hostname)}</strong></li>
        <li><span>IP Adresi:</span> <strong>{html.escape(r.ip_address)}</strong></li>
        <li><span>Web Sunucusu:</span> <strong>{html.escape(r.server)}</strong></li>
        <li><span>Backend / Motor:</span> <strong>{html.escape(r.powered_by or "Gizlenmiş / Yok")}</strong></li>
        <li><span>HTTP Durumu:</span> <strong>{r.status_code}</strong></li>
      </ul>
    </div>

    <!-- SEO & Meta -->
    <div class="card">
      <h2>🏷️ SEO & Meta Verileri</h2>
      <ul class="data-list">
        <li><span>Sayfa Başlığı:</span> <strong>{html.escape(r.meta_title or "Yok")}</strong></li>
        <li><span>Sayfa Dili:</span> <strong>{html.escape(r.language or "Belirtilmemiş")}</strong></li>
        <li><span>Açıklama:</span> <span style="max-width:240px; text-align:right;">{html.escape(r.meta_description or "Yok")}</span></li>
      </ul>
    </div>
  </div>

  <!-- Teknolojiler -->
  <div class="card" style="margin-bottom:24px;">
    <h2>⚡ Tespit Edilen Teknolojiler ({len(r.technologies)})</h2>
    <div style="margin-top:10px;">
      {tech_badges}
    </div>
  </div>

  <!-- Güvenlik Başlıkları Değerlendirmesi -->
  <div class="card" style="margin-bottom:24px;">
    <h2>🛡️ Güvenlik Başlıkları Analizi</h2>
    <div class="table-responsive">
      <table>
        <thead>
          <tr>
            <th>Kural / Başlık</th>
            <th>Durum</th>
            <th>Değer</th>
            <th>Açıklama</th>
          </tr>
        </thead>
        <tbody>
          {sec_rows}
        </tbody>
      </table>
    </div>
  </div>

  <div class="grid">
    <!-- OpenGraph Sosyal Medya -->
    <div class="card">
      <h2>🌐 OpenGraph Sosyal Medya Kartları</h2>
      <div class="table-responsive">
        <table>
          <thead>
            <tr><th>Özellik</th><th>Değer</th></tr>
          </thead>
          <tbody>
            {og_rows}
          </tbody>
        </table>
      </div>
    </div>

    <!-- robots.txt & Sitemap -->
    <div class="card">
      <h2>🤖 robots.txt & Sitemap Keşfi</h2>
      <p style="font-size:13px; margin-bottom:10px;">
        <strong>robots.txt:</strong> {"Bulundu ✅" if r.robots_found else "Bulunamadı ❌"}
      </p>
      <div style="margin-bottom:12px;">
        <span class="text-muted" style="font-size:12px;">Yasaklı Yollar:</span><br>
        {robots_dis}
      </div>
      <span class="text-muted" style="font-size:12px;">Keşfedilen Sayfalar ({len(r.discovered_sitemap_urls)}):</span>
      <div class="sitemap-box">
        <ul>{sitemap_items}</ul>
      </div>
    </div>
  </div>

  <footer style="text-align:center; margin-top:40px; color:var(--muted); font-size:12px;">
    WebClone v2.0 ile otomatik olarak oluşturulmuştur.
  </footer>
</div>
</body>
</html>
"""
