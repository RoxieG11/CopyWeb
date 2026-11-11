<div align="center">

# 🌐 WebClone v2.0 Pro
### Ultra High-Speed, Anonymous Website Cloner & Intelligence Gathering Tool

[![Language](https://img.shields.io/badge/Language-Multi--Language-blue.svg)](#-languages)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)
[![Stealth](https://img.shields.io/badge/Stealth-Anti--Detection-red.svg)](#)

*Clone complete websites with full HTML, CSS, JavaScript, high-resolution images, fonts, media, and data with one click. Generates flawless local offline copies with zero external dependencies.*

---

### 🌐 Languages / Dil Seçimi
[English](README.md) • [Türkçe](docs/translations/README.tr.md) • [Español](docs/translations/README.es.md) • [简体中文](docs/translations/README.zh-CN.md) • [हिन्दी](docs/translations/README.hi.md) • [العربية](docs/translations/README.ar.md) • [Português](docs/translations/README.pt.md) • [Русский](docs/translations/README.ru.md) • [日本語](docs/translations/README.ja.md) • [Deutsch](docs/translations/README.de.md) • [Français](docs/translations/README.fr.md)

---

</div>

## ✨ Key Features

### 1. 🎨 Sleek & Premium Dark Interface (PyQt6)
- **Modern Obsidian & Slate Theme:** Clean, eye-friendly, and modern dark design.
- **Multi-Tab Dashboard:**
  - 🚀 **Dashboard:** Real-time speed metrics, file/page counters, data transfer gauges, and one-click quick actions (*Open Folder*, *index.html*, *Live Preview*, *Target Recon Report*).
  - ⚙️ **Cloning Settings:** Crawl depth (0-3), asset type filters, folder structure (Organized / Mirror), and parallel worker thread allocation.
  - 🕵️ **Stealth & Privacy:** Dynamic User-Agent rotation, Referrer camouflage, human jitter emulation, and proxy/Tor configuration.
  - 🔍 **Target Reconnaissance:** Live server infrastructure cards, CMS/technology stack badges, and security evaluation.
  - 📜 **Live Console:** Color-coded, searchable, and filterable live activity log.
- **Multilingual UI Support:** Change language on the fly (English, Turkish, Spanish, German, Russian, Chinese) directly within the interface.

### 2. ⚡ High-Performance Multi-Threaded Engine
- **Configurable Worker Pool:** 1 to 64 concurrent threads for blisteringly fast asset downloads.
- **HTTP/2 & Keep-Alive:** Pooled connections eliminate handshake overhead.
- **Smart Directory Caching:** Minimizes disk I/O bottlenecks.
- **Compressed Streaming:** Automatic Brotli, Gzip, Deflate, and Zstandard decompression.

### 3. 🔍 Deep Target Reconnaissance & Intelligence
- **Automated Target Analysis Report:**
  - 🖥️ **Infrastructure:** Server IP address, Web Server (Nginx, Apache, Cloudflare, Caddy, etc.), Backend framework.
  - ⚡ **Technology Detection:** WordPress, Shopify, Next.js, React, Vue, Nuxt, Tailwind CSS, Bootstrap, jQuery, and more.
  - 🛡️ **Security Headers Evaluation:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options audit.
  - 🤖 **robots.txt & sitemap.xml Discovery:** Disallowed paths and sitemap URL extraction.
  - 📊 **Standalone HTML & JSON Reports:** Automatically saves `recon_report.json` and a styled `recon_report.html` inside the cloned directory.
- **Rich Asset Discovery:**
  - OpenGraph & Twitter Card images (`og:image`, `twitter:image`).
  - Web App Manifests (`manifest.json`, `site.webmanifest`).
  - Inline JSON state inspection (Next.js `__NEXT_DATA__`, Nuxt `__NUXT__`, Inertia.js).

### 4. 🕵️ Maximum Anonymity & Stealth Mode
- **Realistic Browser Fingerprint Profiles:**
  - Windows 11 Chrome 131, Windows 11 Edge 131, Windows 11 Firefox 132
  - macOS Chrome 131, macOS Safari 18, Linux Firefox 132
- **Dynamic User-Agent Rotation:** Rotates browser identities on every outgoing connection.
- **Accurate Client Hints:** Synchronizes `sec-ch-ua`, `sec-ch-ua-platform`, and `sec-ch-ua-mobile` with the selected profile.
- **Referrer Spoofing:** Mimics incoming traffic from Google, DuckDuckGo, Bing, or self-origin.
- **Proxy & Tor Integration:**
  - Supports HTTP, HTTPS, SOCKS5, and Tor (`socks5h://127.0.0.1:9050`).
  - Built-in one-click live proxy IP & latency testing button.
- **Human Jitter Emulation:** Random millisecond delays to bypass WAF, rate limits, and anti-bot systems.

### 5. 🪟 Windows & Linux Cross-Platform Compatibility
- **Windows Reserved Device Name Guard:** Prevents Windows filesystem errors when encountering `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`.
- **Windows MAX_PATH Protection:** Long filenames and complex queries are hashed and safely clamped.
- **Silent Background Subprocesses:** Uses `CREATE_NO_WINDOW` on Windows to eliminate command prompt flickers.
- **1-Click Launchers:** `run.bat` and `WebClone.bat` for Windows; `run.sh` and `WebClone.desktop` for Linux.

---

## 🚀 Quick Start

### Windows
1. Download or clone this repository.
2. Double-click **`run.bat`** or **`WebClone.bat`**.
   *(Dependencies are checked and installed automatically, then the GUI launches.)*

### Linux / macOS
```bash
# 1. Clone repository
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
./run.sh
# or
python3 gui.py
```

---

## 💻 Command Line Interface (CLI)

```bash
# Clone a single page
python3 clone.py https://example.com

# Crawl 1 level deep and create a ZIP archive
python3 clone.py https://example.com -d 1 --zip

# Clone with exact server directory structure (mirror mode)
python3 clone.py https://example.com --layout mirror

# Full stealth: Tor proxy + Random User-Agent + Google Referrer
python3 clone.py https://example.com --proxy socks5://127.0.0.1:9050 --rotate-ua --referer google

# High speed: 24 parallel worker threads
python3 clone.py https://example.com -w 24 -d 2

# Serve locally upon completion
python3 clone.py https://example.com --serve 8000
```

### CLI Arguments
| Option | Description | Default |
| :--- | :--- | :--- |
| `-d, --depth` | Crawl depth (0 = single page, 1 = + linked pages) | `0` |
| `-w, --workers` | Concurrent worker threads | `16` |
| `--layout` | `organized` (assets/css, assets/img...) or `mirror` | `organized` |
| `--proxy` | Proxy address (`http://...`, `socks5://...`) | `None` |
| `--ua` | User-Agent profile name or `random` | `random` |
| `--rotate-ua` | Rotate User-Agent per connection | `False` |
| `--referer` | Referrer mode (`google`, `duckduckgo`, `bing`, `self`, `none`) | `google` |
| `--delay` | Human delay / jitter between requests (seconds) | `0.0` |
| `--render-js` | Chromium WebEngine rendering for dynamic JavaScript | `False` |
| `--zip` | Build a `.zip` archive on completion | `False` |
| `--serve [PORT]` | Host local clone on HTTP server | `8000` |

---

## 📁 Repository Structure

```
WebClone/
├── clone.py                 # CLI entry point
├── gui.py                   # GUI entry point
├── run.sh                   # Linux 1-click launcher
├── run.bat                  # Windows 1-click launcher
├── WebClone.bat             # Windows batch shortcut
├── WebClone.desktop         # Linux desktop entry
├── build.py                 # Build and packaging tool
├── requirements.txt         # Dependencies
├── pyproject.toml           # Modern package configuration
├── setup.py                 # Package setup script
├── LICENSE                  # MIT License
├── README.md                # English documentation
├── README.tr.md             # Turkish documentation
├── README.es.md             # Spanish documentation
├── README.zh-CN.md          # Chinese documentation
├── README.hi.md             # Hindi documentation
├── README.ar.md             # Arabic documentation
├── README.pt.md             # Portuguese documentation
├── README.ru.md             # Russian documentation
├── README.ja.md             # Japanese documentation
├── README.de.md             # German documentation
├── README.fr.md             # French documentation
├── tests/
│   └── test_clone.py        # Comprehensive test suite
└── webclone/
    ├── __init__.py          # v2.0.0
    ├── core.py              # Download & crawling engine
    ├── gui.py               # Modern PyQt6 GUI
    ├── cli.py               # Command line interface
    ├── i18n.py              # Multilingual localization
    ├── stealth.py           # Anonymity, proxy & UA rotator
    ├── recon.py             # Reconnaissance & HTML reporting
    ├── paths.py             # Windows / Linux path sanitization
    ├── rewrite.py           # HTML / CSS / JS / JSON URL rewriter
    ├── browser.py           # curl HTTP/2 & Chromium WebEngine
    ├── server.py            # Smart local HTTP preview server
    └── icon.svg             # Application icon
```

---

## 📦 Packaging & Distribution

To compile `.whl` and `.tar.gz` distribution packages:

```bash
python3 build.py
```

Packages are output to the `dist/` directory.

---

## 🛡️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
