<div align="center">

# 🌐 WebClone v2.0 Pro
### Yüksek Hızlı, Tam Anonim Web Sitesi Kopyalama ve İstihbarat Aracı

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)
[![Stealth](https://img.shields.io/badge/Stealth-Anti--Detection-red.svg)](#)

*Web sitelerinin tüm HTML, CSS, JavaScript, yüksek çözünürlüklü görsel, font, medya ve verilerini tek tıkla yerel bilgisayarınıza klonlayın. İnternet bağlantısı olmadan birebir çalışan kusursuz yerel kopyalar üretin.*

</div>

---

## ✨ Öne Çıkan Özellikler

### 1. 🎨 Sade ve Premium Arayüz (PyQt6 Dark Mode)
- **Modern Obsidian & Slate Teması:** Gözü yormayan, zarif ve profesyonel koyu tema.
- **Sekmeli Çoklu Panel:**
  - 🚀 **Genel Bakış:** Canlı hız, dosya/sayfa sayaçları, anlık boyut göstergesi ve tek tıkla hızlı aksiyonlar (Klasörü Aç, index.html Aç, Önizle).
  - ⚙️ **Klonlama Ayarları:** Derinlik (0-3), filtreler, klasör düzeni (Organized / Mirror), eşzamanlı worker sayısı.
  - 🕵️ **Gizlilik & Anonimlik:** Gerçek zamanlı User-Agent rotasyonu, Referer kamuflajı, insan taklidi (jitter) ve proxy ayarları.
  - 🔍 **Hedef İstihbarat:** Sunucu altyapısı, CMS/teknoloji tespiti, robots.txt ve sitemap haritası.
  - 📜 **Canlı Konsol:** Renkli, filtrelenebilir ve aranabilir canlı log terminali.

### 2. ⚡ Ultra Hızlı Eşzamanlı İndirme (Multi-Threaded & Pooled)
- **Eşzamanlı Worker Havuzu:** 1'den 64'e kadar ayarlanabilir paralel indirme kanalı.
- **HTTP/2 & Keep-Alive:** Yeniden kullanılabilir oturum havuzları ile sıfır gecikme.
- **Akıllı Dizin Önbellekleme:** Gereksiz disk I/O işlemlerini engelleyen yüksek performanslı dosya yazıcı.
- **Dinamik Sıkıştırma Desteği:** Brotli, Gzip ve Zstandard desteği ile yüksek indirme hızları.

### 3. 🔍 Gelişmiş İstihbarat ve Bilgi Toplama (Reconnaissance)
- **Hedef Analiz Raporu:**
  - 🖥️ **Sunucu & Altyapı:** IP adresi, Web sunucusu (Nginx, Apache, Cloudflare, Caddy vb.), Backend motoru.
  - ⚡ **Teknoloji Tespiti:** WordPress, Shopify, Next.js, React, Vue, Nuxt, Tailwind CSS, Bootstrap, jQuery ve daha fazlası.
  - 🛡️ **Güvenlik Başlıkları:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options analizi.
  - 🤖 **robots.txt & sitemap.xml Keşfi:** Gizli veya izin verilmeyen yollar ile sitemap URL'lerinin otomatik taranması.
  - 📊 **Otomatik Raporlama:** Her klonlamada hedef klasöre `recon_report.json` ve şık, bağımsız bir `recon_report.html` raporu kaydedilir.
- **Zenginleştirilmiş Varlık Keşfi:**
  - OpenGraph ve Twitter Card görselleri (`og:image`, `twitter:image`).
  - Web App Manifest (`manifest.json`, `site.webmanifest`).
  - Next.js (`__NEXT_DATA__`), Nuxt (`__NUXT__`) ve Inertia.js JSON veri bloklarındaki gizli varlık URL'leri.

### 4. 🕵️ Maksimum Anonimlik ve Stealth Modu
- **Modern Tarayıcı Parmak İzi Havuzu:**
  - Windows 11 Chrome 131, Windows 11 Edge 131, Windows 11 Firefox 132
  - macOS Chrome 131, macOS Safari 18, Linux Firefox 132
- **Dinamik User-Agent Rotasyonu:** Her istekte farklı tarayıcı profili taklit edebilme.
- **Client Hints Eşleşmesi:** `sec-ch-ua`, `sec-ch-ua-platform`, `sec-ch-ua-mobile` başlıklarının seçilen tarayıcıyla %100 uyumu.
- **Referer Kamuflajı:** İstekleri Google, DuckDuckGo veya Bing üzerinden geliyormuş gibi gösterme.
- **Proxy / Tor Desteği:**
  - HTTP, HTTPS, SOCKS5 ve Tor (`socks5h://127.0.0.1:9050`) desteği.
  - Arayüzden tek tıkla canlı IP ve gecikme testi.
- **İnsan Benzetimi (Jitter):** Bot engellerini ve WAF/DDoS korumalarını aşmak için rastgele milisaniyelik istek gecikmeleri.

### 5. 🪟 Windows ve Linux Tam Çapraz Platform Uyumluluğu
- **Windows Ayrılmış Aygıt Adları Koruması:** `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9` adlarındaki sayfalar Windows'ta çökme olmadan güvenle kaydedilir.
- **Windows MAX_PATH Koruması:** Aşırı uzun dosya ve URL parçaları akıllıca hash'lenerek kırpılır.
- **Görünmez Konsol Çalıştırma:** Windows'ta curl ve Chromium arka plan süreçleri `CREATE_NO_WINDOW` ile siyah pencere açmadan sessizce çalışır.
- **Tek Tıkla Çalıştırma:** Windows için `run.bat` ve `WebClone.bat`, Linux için `run.sh` ve `.desktop` kısayolu.

---

## 🚀 Hızlı Başlangıç

### Windows Kurulumu ve Çalıştırma
1. Bu depoyu indirin veya klonlayın.
2. Klasör içindeki **`run.bat`** veya **`WebClone.bat`** dosyasına çift tıklayın!
   *(Gerekli kütüphaneler otomatik olarak kontrol edilir ve arayüz başlatılır.)*

### Linux / macOS Kurulumu ve Çalıştırma
```bash
# 1. Depoyu klonlayın
git clone https://github.com/yourusername/webclone.git
cd webclone

# 2. Gereksinimleri yükleyin
pip install -r requirements.txt

# 3. Başlatın
./run.sh
# veya
python3 gui.py
```

---

## 💻 Komut Satırı (CLI) Kullanımı

Terminalden hızlıca klonlama yapmak için zengin CLI parametreleri mevcuttur:

```bash
# Tek sayfayı indir (output/<domain>/ klasörüne)
python3 clone.py https://example.com

# 1 seviye derinlikte bağlantılı sayfaları da indir ve bitince .zip yap
python3 clone.py https://example.com -d 1 --zip

# Birebir sunucu klasör yapısıyla indir (mirror modu)
python3 clone.py https://example.com --layout mirror

# Tam anonimlik: Tor proxy + Rastgele UA rotasyonu + Google Referer
python3 clone.py https://example.com --proxy socks5://127.0.0.1:9050 --rotate-ua --referer google

# 24 paralel iş parçacığıyla yüksek hızlı indirme
python3 clone.py https://example.com -w 24 -d 2

# İndirme bitince otomatik olarak yerel HTTP sunucusu aç
python3 clone.py https://example.com --serve 8000
```

### CLI Parametreleri Tablosu
| Parametre | Açıklama | Varsayılan |
| :--- | :--- | :--- |
| `-d, --depth` | Bağlantı takip derinliği (0=sadece verilen sayfa, 1=+bağlantılar) | `0` |
| `-w, --workers` | Eşzamanlı iş parçacığı (worker) sayısı | `16` |
| `--layout` | Klasör düzeni: `organized` veya `mirror` | `organized` |
| `--proxy` | Vekil sunucu adresi (`http://...`, `socks5://...`) | `None` |
| `--ua` | User-Agent profili veya `random` | `random` |
| `--rotate-ua` | Her istekte User-Agent değiştir | `False` |
| `--referer` | Referer modu (`google`, `duckduckgo`, `bing`, `self`, `none`) | `google` |
| `--delay` | İstekler arası insan gecikmesi (saniye) | `0.0` |
| `--render-js` | JavaScript korumalı siteler için dahili Chromium motoru | `False` |
| `--zip` | İşlem bittiğinde `.zip` arşivi oluştur | `False` |
| `--serve [PORT]` | Klonlanan siteyi yerel canlı sunucuda yayınla | `8000` |

---

## 📁 Proje Dizin Yapısı

```
WebClone/
├── clone.py                 # CLI başlatıcı
├── gui.py                   # GUI başlatıcı
├── run.sh                   # Linux 1-tık çalıştırıcı
├── run.bat                  # Windows 1-tık çalıştırıcı
├── WebClone.bat             # Windows kısayolu
├── WebClone.desktop         # Linux masaüstü kısayolu
├── build.py                 # Derleme ve paketleme aracı
├── requirements.txt         # Bağımlılıklar
├── pyproject.toml           # Modern paket yapılandırması
├── setup.py                 # Setuptools yapılandırması
├── LICENSE                  # MIT Lisansı
├── README.md                # Kapsamlı dökümantasyon
├── tests/
│   └── test_clone.py        # Kapsamlı birim testleri
└── webclone/
    ├── __init__.py          # Paket tanımı (v2.0.0)
    ├── core.py              # Klonlama ve indirme çekirdeği
    ├── gui.py               # PyQt6 Premium grafik arayüzü
    ├── cli.py               # Komut satırı arayüzü
    ├── stealth.py           # Gizlilik, anonimlik ve proxy yöneticisi
    ├── recon.py             # Hedef istihbarat ve HTML rapor motoru
    ├── paths.py             # Çapraz platform ve Windows dosya yolu yöneticisi
    ├── rewrite.py           # HTML, CSS, JS ve JSON URL yerelleştiricisi
    ├── browser.py           # curl HTTP/2 ve Chromium WebEngine katmanı
    ├── server.py            # Akıllı yerel HTTP önizleme sunucusu
    └── icon.svg             # Uygulama logosu
```

---

## 📦 Dağıtım ve Paketleme

Projeyi `.whl` ve `.tar.gz` formatlarında derlemek için:

```bash
python3 build.py
```

Derlenen dosyalar `dist/` klasörüne aktarılacaktır.

---

## 🛡️ Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
