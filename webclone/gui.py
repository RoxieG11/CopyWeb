"""WebClone v2.0 Premium Masaüstü Arayüzü (GUI)."""
from __future__ import annotations

import os
import shutil
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlsplit

from PyQt6.QtCore import QObject, QTimer, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .core import CloneOptions, CloneResult, Cloner
from .recon import ReconReport
from .server import PreviewServer
from .stealth import PROFILES, StealthManager

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = BASE_DIR / "output"

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* Sekmeler (QTabWidget) */
QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 10px;
    background-color: #0f172a;
    top: -1px;
}
QTabBar::tab {
    background-color: #111827;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 18px;
    margin-right: 4px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border-color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}
QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #cbd5e1;
}

/* Kartlar */
QFrame#card {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
}
QFrame#statCard {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 6px;
}
QFrame#statCard:hover {
    border-color: #334155;
    background-color: #162032;
}

/* Başlıklar */
QLabel#brandTitle {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
QLabel#brandTag {
    background-color: #0369a1;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
QLabel#statusPill {
    background-color: #1e293b;
    color: #38bdf8;
    border: 1px solid #0284c7;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}
QLabel#statValue {
    font-size: 19px;
    font-weight: 700;
    color: #38bdf8;
}
QLabel#statLabel {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
}

/* Girdi Alanları */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #0b0f19;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 9px 12px;
    color: #f8fafc;
    selection-background-color: #0284c7;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38bdf8;
    background-color: #0e1526;
}
QLineEdit#heroInput {
    font-size: 14px;
    padding: 10px 14px;
    border: 1px solid #0284c7;
    background-color: #090e1a;
}

/* Butonlar */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    border: 1px solid #38bdf8;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    padding: 10px 24px;
    border-radius: 8px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #1d4ed8);
}
QPushButton#dangerBtn {
    background-color: #991b1b;
    border: 1px solid #ef4444;
    color: #ffffff;
}
QPushButton#dangerBtn:hover {
    background-color: #7f1d1d;
}
QPushButton#successBtn {
    background-color: #065f46;
    border: 1px solid #10b981;
    color: #ffffff;
}
QPushButton#successBtn:hover {
    background-color: #047857;
}
QPushButton:disabled,
QPushButton#primaryBtn:disabled,
QPushButton#dangerBtn:disabled,
QPushButton#successBtn:disabled {
    background-color: #162032;
    color: #64748b;
    border: 1px solid #1e293b;
}

/* İlerleme Çubuğu */
QProgressBar {
    background-color: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 8px;
    text-align: center;
    color: #f8fafc;
    font-weight: 700;
    font-size: 12px;
    min-height: 24px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 7px;
}

/* Konsol Günlüğü */
QPlainTextEdit {
    background-color: #070a12;
    border: 1px solid #1e293b;
    border-radius: 8px;
    color: #cbd5e1;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
    padding: 10px;
    line-height: 1.4;
}

QCheckBox {
    spacing: 8px;
    color: #cbd5e1;
    font-weight: 500;
}
QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0b0f19;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

QGroupBox {
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 700;
    color: #38bdf8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 4px;
}
"""


def _make_app_icon() -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#0284c7"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(4, 4, 56, 56, 14, 14)
    p.setPen(QColor("#ffffff"))
    font = QFont("Sans", 24, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "W")
    p.end()
    return QIcon(pix)


class CloneWorker(QObject):
    """Arka planda Cloner çalıştıran sinyal köprüsü."""

    event_received = pyqtSignal(str, dict)
    finished = pyqtSignal(object, str)

    def __init__(self, url: str, output_dir: Path, opts: CloneOptions, make_zip: bool):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.opts = opts
        self.make_zip = make_zip
        self.cancel_event = threading.Event()

    def cancel(self) -> None:
        self.cancel_event.set()

    def start_in_thread(self) -> threading.Thread:
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        return t

    def _run(self) -> None:
        cloner = Cloner(
            self.url,
            self.output_dir,
            self.opts,
            on_event=lambda name, data: self.event_received.emit(name, data),
            cancel_event=self.cancel_event,
        )
        result = cloner.run()
        zip_path = ""
        if self.make_zip and result.pages and not result.cancelled:
            try:
                zip_path = shutil.make_archive(str(result.output_dir), "zip", result.output_dir)
            except Exception as e:  # noqa: BLE001
                self.event_received.emit("asset_failed", {"url": "ZIP", "error": str(e)})
        self.finished.emit(result, zip_path)


class StatBox(QFrame):
    def __init__(self, label: str, initial: str = "0") -> None:
        super().__init__()
        self.setObjectName("statCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(2)
        self.val_lbl = QLabel(initial)
        self.val_lbl.setObjectName("statValue")
        self.lbl = QLabel(label)
        self.lbl.setObjectName("statLabel")
        lay.addWidget(self.val_lbl)
        lay.addWidget(self.lbl)

    def set_value(self, text: str) -> None:
        self.val_lbl.setText(text)


class MainWindow(QMainWindow):
    def __init__(self, initial_url: str = "") -> None:
        super().__init__()
        self.setWindowTitle("WebClone v2.0 Pro — Web Sitesi Kopyalama & İstihbarat Aracı")
        self.setWindowIcon(_make_app_icon())
        self.resize(1000, 750)
        self.setStyleSheet(STYLESHEET)

        self._worker: CloneWorker | None = None
        self._last_result: CloneResult | None = None
        self._last_zip: str = ""
        self._custom_out = False
        self._t0 = 0.0
        self._pages_count = 0
        self._assets_done = 0
        self._assets_total = 0
        self._total_bytes = 0
        self._errors_count = 0
        self._preview = PreviewServer()

        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._tick_timer)

        self._build_ui()
        if initial_url:
            self.url_edit.setText(initial_url)
        else:
            self._update_default_output("")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        # 1. Üst Başlık ve Durum Çubuğu
        header = QHBoxLayout()
        title_box = QHBoxLayout()
        title_box.setSpacing(10)
        title_lbl = QLabel("WebClone")
        title_lbl.setObjectName("brandTitle")
        tag_lbl = QLabel("v2.0 PRO")
        tag_lbl.setObjectName("brandTag")
        title_box.addWidget(title_lbl)
        title_box.addWidget(tag_lbl)
        header.addLayout(title_box)

        header.addStretch()
        self.status_pill = QLabel("HAZIR")
        self.status_pill.setObjectName("statusPill")
        header.addWidget(self.status_pill)
        root.addLayout(header)

        # 2. Hero URL Kartı
        hero_card = QFrame()
        hero_card.setObjectName("card")
        hero_lay = QVBoxLayout(hero_card)
        hero_lay.setContentsMargins(14, 12, 14, 12)
        hero_lay.setSpacing(10)

        url_row = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setObjectName("heroInput")
        self.url_edit.setPlaceholderText("https://site.com (Kopyalanacak web sitesinin adresini yapıştırın)")
        self.url_edit.textChanged.connect(self._on_url_changed)
        self.url_edit.returnPressed.connect(self._start_clone)

        paste_btn = QPushButton("📋 Yapıştır")
        paste_btn.setToolTip("Panodan yapıştır")
        paste_btn.clicked.connect(self._paste_url)

        self.start_btn = QPushButton("🚀 Klonlamayı Başlat")
        self.start_btn.setObjectName("primaryBtn")
        self.start_btn.clicked.connect(self._start_clone)

        self.stop_btn = QPushButton("⏹ Durdur")
        self.stop_btn.setObjectName("dangerBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_clone)

        url_row.addWidget(self.url_edit, 1)
        url_row.addWidget(paste_btn)
        url_row.addWidget(self.start_btn)
        url_row.addWidget(self.stop_btn)
        hero_lay.addLayout(url_row)

        # Çıktı Klasörü
        out_row = QHBoxLayout()
        out_lbl = QLabel("Kayıt Klasörü:")
        out_lbl.setStyleSheet("font-weight: 600; color: #94a3b8;")
        self.out_edit = QLineEdit()
        self.out_edit.textEdited.connect(self._on_output_edited)
        self.out_edit.textChanged.connect(self._refresh_action_buttons)
        browse_btn = QPushButton("Klasör Seç...")
        browse_btn.clicked.connect(self._browse_output)
        out_row.addWidget(out_lbl)
        out_row.addWidget(self.out_edit, 1)
        out_row.addWidget(browse_btn)
        hero_lay.addLayout(out_row)
        root.addWidget(hero_card)

        # 3. Sekmeli Ana Bölüm (Tabs)
        self.tabs = QTabWidget()

        # TAB 1: Kontrol Paneli (Dashboard)
        tab_dashboard = QWidget()
        dash_lay = QVBoxLayout(tab_dashboard)
        dash_lay.setContentsMargins(14, 14, 14, 14)
        dash_lay.setSpacing(12)

        # İstatistik Kartları
        stats_row = QHBoxLayout()
        self.stat_pages = StatBox("SAYFA SAYISI", "0")
        self.stat_assets = StatBox("İNDİRİLEN DOSYA", "0 / 0")
        self.stat_size = StatBox("TOPLAM BOYUT", "0 KB")
        self.stat_time = StatBox("GEÇEN SÜRE", "0.0 sn")
        self.stat_errors = StatBox("HATA SAYISI", "0")
        stats_row.addWidget(self.stat_pages)
        stats_row.addWidget(self.stat_assets)
        stats_row.addWidget(self.stat_size)
        stats_row.addWidget(self.stat_time)
        stats_row.addWidget(self.stat_errors)
        dash_lay.addLayout(stats_row)

        # İlerleme Çubuğu
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("Hazır — Bir URL girip 'Klonlamayı Başlat'a tıklayın")
        dash_lay.addWidget(self.progress)

        # Hızlı Aksiyon Butonları
        actions = QHBoxLayout()
        self.open_folder_btn = QPushButton("📁 Klasörü Aç")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_folder)

        self.preview_btn = QPushButton("🌐 Canlı Sunucuda Önizle")
        self.preview_btn.setObjectName("successBtn")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._open_preview)

        self.open_html_btn = QPushButton("📄 index.html Aç")
        self.open_html_btn.setEnabled(False)
        self.open_html_btn.clicked.connect(self._open_index_html)

        self.open_recon_btn = QPushButton("🔍 İstihbarat Raporu")
        self.open_recon_btn.setEnabled(False)
        self.open_recon_btn.clicked.connect(self._open_recon_report)

        actions.addWidget(self.open_folder_btn)
        actions.addWidget(self.preview_btn)
        actions.addWidget(self.open_html_btn)
        actions.addWidget(self.open_recon_btn)
        actions.addStretch()
        dash_lay.addLayout(actions)

        # Canlı mini akış
        dash_log_lbl = QLabel("Canlı İşlem Akışı:")
        dash_log_lbl.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 11px;")
        dash_lay.addWidget(dash_log_lbl)
        self.dash_log = QPlainTextEdit()
        self.dash_log.setReadOnly(True)
        self.dash_log.setMaximumBlockCount(1000)
        self.dash_log.setPlaceholderText("İşlem başladığında anlık durum burada akacaktır...")
        dash_lay.addWidget(self.dash_log, 1)

        self.tabs.addTab(tab_dashboard, "🚀 Genel Bakış")

        # TAB 2: Klonlama Ayarları
        tab_settings = QWidget()
        set_lay = QVBoxLayout(tab_settings)
        set_lay.setContentsMargins(14, 14, 14, 14)
        set_lay.setSpacing(12)

        set_grid = QGridLayout()
        set_grid.setHorizontalSpacing(16)
        set_grid.setVerticalSpacing(10)

        set_grid.addWidget(QLabel("Link Derinliği:"), 0, 0)
        self.depth_combo = QComboBox()
        self.depth_combo.addItem("0 — Sadece Bu Sayfa (Hızlı)", 0)
        self.depth_combo.addItem("1 — + Bağlantılı Sayfalar (Önerilen)", 1)
        self.depth_combo.addItem("2 — 2 Seviye Derinlik", 2)
        self.depth_combo.addItem("3 — Tüm Siteyi Gez (3 Seviye)", 3)
        self.depth_combo.setCurrentIndex(1)
        set_grid.addWidget(self.depth_combo, 0, 1)

        set_grid.addWidget(QLabel("Klasör Düzeni:"), 0, 2)
        self.layout_combo = QComboBox()
        self.layout_combo.addItem("Düzenli (assets/css, assets/img, ...)", "organized")
        self.layout_combo.addItem("Birebir Ayna (Sunucu klasör yapısı)", "mirror")
        set_grid.addWidget(self.layout_combo, 0, 3)

        set_grid.addWidget(QLabel("Maksimum Sayfa:"), 1, 0)
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 5000)
        self.max_pages_spin.setValue(50)
        set_grid.addWidget(self.max_pages_spin, 1, 1)

        set_grid.addWidget(QLabel("Paralel İndirme (Workers):"), 1, 2)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 64)
        self.workers_spin.setValue(16)
        set_grid.addWidget(self.workers_spin, 1, 3)

        set_grid.addWidget(QLabel("Zaman Aşımı (sn):"), 2, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(3, 60)
        self.timeout_spin.setValue(12)
        set_grid.addWidget(self.timeout_spin, 2, 1)
        set_lay.addLayout(set_grid)

        # Filtreleme Grubu
        filter_group = QGroupBox("İndirilecek Varlık Türleri")
        filter_lay = QGridLayout(filter_group)
        self.chk_images = QCheckBox("Görseller (PNG, JPG, WebP, SVG, AVIF vb.)")
        self.chk_images.setChecked(True)
        self.chk_styles = QCheckBox("Stil Dosyaları (CSS, Less vb.)")
        self.chk_styles.setChecked(True)
        self.chk_scripts = QCheckBox("Scriptler (JavaScript, JSON)")
        self.chk_scripts.setChecked(True)
        self.chk_fonts = QCheckBox("Fontlar (WOFF2, WOFF, TTF vb.)")
        self.chk_fonts.setChecked(True)
        self.chk_media = QCheckBox("Medya & Ses (MP4, WebM, MP3 vb.)")
        self.chk_media.setChecked(True)
        self.chk_docs = QCheckBox("Belgeler (PDF, TXT, XML vb.)")
        self.chk_docs.setChecked(True)

        filter_lay.addWidget(self.chk_images, 0, 0)
        filter_lay.addWidget(self.chk_styles, 0, 1)
        filter_lay.addWidget(self.chk_scripts, 1, 0)
        filter_lay.addWidget(self.chk_fonts, 1, 1)
        filter_lay.addWidget(self.chk_media, 2, 0)
        filter_lay.addWidget(self.chk_docs, 2, 1)
        set_lay.addWidget(filter_group)

        # Diğer Seçenekler
        extra_group = QGroupBox("Genel Seçenekler")
        extra_lay = QVBoxLayout(extra_group)
        self.ext_check = QCheckBox("CDN / Dış alan adı dosyalarını da indir")
        self.ext_check.setChecked(True)
        self.render_js_check = QCheckBox("Tarayıcı Motoru (Chromium WebEngine ile JS ve Lazy-load Görselleri Aç)")
        self.zip_check = QCheckBox("Bittiğinde .zip arşivi oluştur")
        self.zip_check.setChecked(True)
        self.recon_check = QCheckBox("Hedef İstihbarat Raporu ve Teknoloji Analizini Otomatik Oluştur")
        self.recon_check.setChecked(True)
        extra_lay.addWidget(self.ext_check)
        extra_lay.addWidget(self.render_js_check)
        extra_lay.addWidget(self.zip_check)
        extra_lay.addWidget(self.recon_check)
        set_lay.addWidget(extra_group)
        set_lay.addStretch()

        self.tabs.addTab(tab_settings, "⚙️ Ayarlar")

        # TAB 3: Gizlilik & Anonimlik (Stealth)
        tab_stealth = QWidget()
        stealth_lay = QVBoxLayout(tab_stealth)
        stealth_lay.setContentsMargins(14, 14, 14, 14)
        stealth_lay.setSpacing(14)

        ua_group = QGroupBox("User-Agent & Tarayıcı Kimliği")
        ua_lay = QGridLayout(ua_group)
        ua_lay.addWidget(QLabel("Tarayıcı Profili:"), 0, 0)
        self.ua_combo = QComboBox()
        self.ua_combo.addItem("🎲 Rastgele (Her İstekte Değiştir)", "random")
        for prof in PROFILES:
            self.ua_combo.addItem(f"💻 {prof.name}", prof.name)
        ua_lay.addWidget(self.ua_combo, 0, 1)

        self.rotate_ua_check = QCheckBox("Her bağlantıda farklı tarayıcı profili taklit et (Dinamik Parmak İzi)")
        self.rotate_ua_check.setChecked(True)
        ua_lay.addWidget(self.rotate_ua_check, 1, 0, 1, 2)
        stealth_lay.addWidget(ua_group)

        # Referer & Ağ Kamuflajı
        cam_group = QGroupBox("Ağ Kamuflajı & İnsan Taklidi")
        cam_lay = QGridLayout(cam_group)
        cam_lay.addWidget(QLabel("Referer (Yönlendiren):"), 0, 0)
        self.referer_combo = QComboBox()
        self.referer_combo.addItem("Google Arama (https://www.google.com/)", "google")
        self.referer_combo.addItem("DuckDuckGo (https://duckduckgo.com/)", "duckduckgo")
        self.referer_combo.addItem("Bing (https://www.bing.com/)", "bing")
        self.referer_combo.addItem("Hedef Sitenin Kendisi (Self-Origin)", "self")
        self.referer_combo.addItem("Boş / Gönderme (Temiz)", "none")
        cam_lay.addWidget(self.referer_combo, 0, 1)

        cam_lay.addWidget(QLabel("İnsan Gecikmesi / Jitter (sn):"), 1, 0)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 5.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setValue(0.0)
        self.delay_spin.setToolTip("İstekler arasına rastgele milisaniyelik gecikme ekleyerek WAF/bot korumalarını atlatır")
        cam_lay.addWidget(self.delay_spin, 1, 1)
        stealth_lay.addWidget(cam_group)

        # Proxy Grubu
        proxy_group = QGroupBox("Vekil Sunucu (Proxy / Tor Desteği)")
        proxy_lay = QGridLayout(proxy_group)
        proxy_lay.addWidget(QLabel("Proxy Adresi:"), 0, 0)
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText("socks5://127.0.0.1:9050  veya  http://ip:port")
        proxy_lay.addWidget(self.proxy_edit, 0, 1)

        self.test_proxy_btn = QPushButton("🔌 Bağlantıyı Test Et")
        self.test_proxy_btn.clicked.connect(self._test_proxy)
        proxy_lay.addWidget(self.test_proxy_btn, 0, 2)

        self.proxy_status_lbl = QLabel("Tor veya HTTP/HTTPS/SOCKS5 vekil sunucusu ile tam anonimlik sağlayın.")
        self.proxy_status_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        proxy_lay.addWidget(self.proxy_status_lbl, 1, 0, 1, 3)
        stealth_lay.addWidget(proxy_group)
        stealth_lay.addStretch()

        self.tabs.addTab(tab_stealth, "🕵️ Gizlilik & Anonimlik")

        # TAB 4: Hedef İstihbarat & Bilgi Toplama (Recon)
        tab_recon = QWidget()
        recon_lay = QVBoxLayout(tab_recon)
        recon_lay.setContentsMargins(14, 14, 14, 14)
        recon_lay.setSpacing(12)

        self.recon_view = QPlainTextEdit()
        self.recon_view.setReadOnly(True)
        self.recon_view.setPlaceholderText(
            "Hedef web sitesinin IP adresi, sunucusu, CMS ve altyapı teknolojileri, robots.txt kuralları "
            "ve güvenlik değerlendirmesi kopyalama başladığında burada listelenecektir..."
        )
        recon_lay.addWidget(self.recon_view, 1)

        recon_btns = QHBoxLayout()
        self.open_html_report_btn = QPushButton("🌐 Şık HTML Raporunu Tarayıcıda Aç")
        self.open_html_report_btn.setObjectName("successBtn")
        self.open_html_report_btn.setEnabled(False)
        self.open_html_report_btn.clicked.connect(self._open_recon_report)
        recon_btns.addWidget(self.open_html_report_btn)
        recon_btns.addStretch()
        recon_lay.addLayout(recon_btns)

        self.tabs.addTab(tab_recon, "🔍 Hedef İstihbarat")

        # TAB 5: Ayrıntılı Canlı Günlük (Live Console)
        tab_log = QWidget()
        log_lay = QVBoxLayout(tab_log)
        log_lay.setContentsMargins(14, 14, 14, 14)
        log_lay.setSpacing(10)

        log_tools = QHBoxLayout()
        self.log_filter = QLineEdit()
        self.log_filter.setPlaceholderText("Günlük içinde filtrele / ara (örn: .png, HATA)...")
        self.log_filter.textChanged.connect(self._apply_log_filter)
        clear_btn = QPushButton("Temizle")
        clear_btn.clicked.connect(self._clear_logs)
        log_tools.addWidget(self.log_filter, 1)
        log_tools.addWidget(clear_btn)
        log_lay.addLayout(log_tools)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(3000)
        log_lay.addWidget(self.log_box, 1)

        self.tabs.addTab(tab_log, "📜 Canlı Konsol")

        root.addWidget(self.tabs, 1)

    # ------------------------------------------------------------ Yardımcılar
    def _current_out_dir(self) -> Path:
        return Path(self.out_edit.text().strip() or str(DEFAULT_OUTPUT_ROOT / "site"))

    def _refresh_action_buttons(self) -> None:
        if self._worker is not None:
            return
        d = self._current_out_dir()
        has_dir = d.is_dir()
        has_index = (d / "index.html").is_file()
        has_recon = (d / "recon_report.html").is_file()
        self.open_folder_btn.setEnabled(has_dir)
        self.preview_btn.setEnabled(has_index)
        self.open_html_btn.setEnabled(has_index)
        self.open_recon_btn.setEnabled(has_recon)
        self.open_html_report_btn.setEnabled(has_recon)

    def _paste_url(self) -> None:
        text = QApplication.clipboard().text().strip()
        if text:
            self.url_edit.setText(text)

    def _on_url_changed(self, text: str) -> None:
        if not self._custom_out:
            self._update_default_output(text)

    def _on_output_edited(self) -> None:
        self._custom_out = bool(self.out_edit.text().strip())

    def _update_default_output(self, url: str) -> None:
        raw = url.strip()
        if raw and "://" not in raw:
            raw = "https://" + raw
        host = urlsplit(raw).hostname if raw else None
        if host and host.startswith("www."):
            host = host[4:]
        target = DEFAULT_OUTPUT_ROOT / (host or "site")
        self.out_edit.setText(str(target))

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kayıt Klasörü Seçin", self.out_edit.text())
        if folder:
            self._custom_out = True
            self.out_edit.setText(folder)

    def _log(self, msg: str) -> None:
        self.dash_log.appendPlainText(msg)
        self.log_box.appendPlainText(msg)

    def _clear_logs(self) -> None:
        self.dash_log.clear()
        self.log_box.clear()

    def _apply_log_filter(self, query: str) -> None:
        pass  # Basit tutuldu

    def _tick_timer(self) -> None:
        elapsed = time.monotonic() - self._t0
        self.stat_time.set_value(f"{elapsed:.1f} sn")

    def _test_proxy(self) -> None:
        proxy = self.proxy_edit.text().strip()
        if not proxy:
            QMessageBox.information(self, "Bilgi", "Lütfen önce test edilecek bir vekil sunucu adresi girin.")
            return

        self.proxy_status_lbl.setText("🔄 Vekil sunucu test ediliyor...")
        self.test_proxy_btn.setEnabled(False)

        def run_test():
            res = StealthManager.test_proxy(proxy)
            QTimer.singleShot(0, lambda: self._on_proxy_tested(res))

        threading.Thread(target=run_test, daemon=True).start()

    def _on_proxy_tested(self, res: dict) -> None:
        self.test_proxy_btn.setEnabled(True)
        if res["ok"]:
            self.proxy_status_lbl.setText(
                f"✅ Başarılı! Dış IP: {res['ip']}  (Gecikme: {res['latency']} ms)"
            )
            self.proxy_status_lbl.setStyleSheet("color: #34d399; font-weight: 600; font-size: 11px;")
        else:
            self.proxy_status_lbl.setText(f"❌ Bağlantı başarısız: {res['error']}")
            self.proxy_status_lbl.setStyleSheet("color: #f87171; font-weight: 600; font-size: 11px;")

    # ------------------------------------------------------------ Klonlama
    def _start_clone(self) -> None:
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen kopyalanacak web sitesinin adresini girin.")
            self.url_edit.setFocus()
            return

        if not self._custom_out:
            self._update_default_output(url)
        out_dir = self._current_out_dir()

        opts = CloneOptions(
            depth=int(self.depth_combo.currentData()),
            max_pages=self.max_pages_spin.value(),
            workers=self.workers_spin.value(),
            timeout=float(self.timeout_spin.value()),
            layout=str(self.layout_combo.currentData()),
            external_assets=self.ext_check.isChecked(),
            verify_ssl=False,
            render_js=self.render_js_check.isChecked(),
            user_agent_profile=str(self.ua_combo.currentData()),
            rotate_ua=self.rotate_ua_check.isChecked(),
            proxy=self.proxy_edit.text().strip() or None,
            referer_mode=str(self.referer_combo.currentData()),
            min_delay=self.delay_spin.value(),
            max_delay=self.delay_spin.value() * 1.5 if self.delay_spin.value() > 0 else 0.0,
            collect_recon=self.recon_check.isChecked(),
            download_images=self.chk_images.isChecked(),
            download_styles=self.chk_styles.isChecked(),
            download_scripts=self.chk_scripts.isChecked(),
            download_fonts=self.chk_fonts.isChecked(),
            download_media=self.chk_media.isChecked(),
            download_documents=self.chk_docs.isChecked(),
        )

        self._pages_count = 0
        self._assets_done = 0
        self._assets_total = 0
        self._total_bytes = 0
        self._errors_count = 0
        self._last_result = None
        self._last_zip = ""
        self.stat_pages.set_value("0")
        self.stat_assets.set_value("0 / 0")
        self.stat_size.set_value("0 KB")
        self.stat_errors.set_value("0")
        self.stat_time.set_value("0.0 sn")
        self.progress.setRange(0, 0)
        self.progress.setFormat("Siteye güvenli şekilde bağlanılıyor...")
        self.status_pill.setText("BAĞLANILIYOR")
        self.status_pill.setStyleSheet("background-color: #0284c7; color: #ffffff;")
        self._clear_logs()
        self.recon_view.clear()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.open_html_btn.setEnabled(False)
        self.open_recon_btn.setEnabled(False)
        self.open_html_report_btn.setEnabled(False)

        self._t0 = time.monotonic()
        self._timer.start()

        self._worker = CloneWorker(url, out_dir, opts, self.zip_check.isChecked())
        self._worker.event_received.connect(self._on_clone_event)
        self._worker.finished.connect(self._on_clone_finished)
        self._worker.start_in_thread()

    def _stop_clone(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._log("⏹ İptal isteği gönderildi, aktif işlemler durduruluyor...")
            self.stop_btn.setEnabled(False)
            self.status_pill.setText("DURDURULUYOR")

    def _on_clone_event(self, name: str, data: dict) -> None:
        if name == "start":
            self.status_pill.setText("KLONLANIYOR")
            self._log(f"🚀 Klonlama Başlatıldı: {data['url']}")
            self._log(f"📁 Kayıt Klasörü: {data['output_dir']}\n")
        elif name == "recon_done":
            rep: ReconReport = data.get("report")
            if rep:
                self._update_recon_ui(rep)
        elif name == "page_start":
            self._log(f"📄 [SAYFA] İndiriliyor: {data['url']}  →  {data['path']}")
        elif name == "page_done":
            self._pages_count += 1
            self.stat_pages.set_value(str(self._pages_count))
        elif name == "page_failed":
            self._errors_count += 1
            self.stat_errors.set_value(str(self._errors_count))
            self._log(f"❌ [SAYFA HATASI] {data['url']} — {data['error']}")
        elif name == "asset_queued":
            self._assets_total = data["total"]
            self._update_progress()
        elif name == "asset_done":
            self._assets_done = data["done"]
            self._assets_total = data["total"]
            size = data.get("size", 0)
            self._total_bytes += size
            self._update_progress()
            size_kb = size / 1024
            kind = data["kind"].upper()
            self._log(f"  ✓ [{kind:5}] {data['path']} ({size_kb:.1f} KB)")
        elif name == "asset_failed":
            self._errors_count += 1
            self.stat_errors.set_value(str(self._errors_count))
            self._log(f"  ⚠ [HATA] {data['url']} — {data['error']}")

    def _update_recon_ui(self, rep: ReconReport) -> None:
        techs = ", ".join(t["name"] for t in rep.technologies) or "Tespit edilemedi"
        text = f"""🔍 HEDEF İSTİHBARAT RAPORU
==================================================
• Hedef URL     : {rep.target_url}
• Alan Adı      : {rep.hostname}
• IP Adresi     : {rep.ip_address}
• Web Sunucusu  : {rep.server}
• Backend Motor : {rep.powered_by or 'Gizlenmiş'}
• Sayfa Başlığı : {rep.meta_title or 'Yok'}
• Dil           : {rep.language or 'Belirtilmemiş'}
• Teknolojiler  : {techs}
• robots.txt    : {'Bulundu' if rep.robots_found else 'Yok'}
==================================================
Güvenlik Başlıkları Analizi:
"""
        for s in rep.security_headers:
            status = "✅ Aktif" if s["present"] else "❌ Eksik"
            text += f"  [{status}] {s['title']} ({s['header']})\n"
        self.recon_view.setPlainText(text)
        self._log("🔍 Hedef web sitesinin istihbarat ve teknoloji analizi tamamlandı.")

    def _update_progress(self) -> None:
        self.stat_assets.set_value(f"{self._assets_done} / {self._assets_total}")
        if self._total_bytes > 1024 * 1024:
            self.stat_size.set_value(f"{self._total_bytes / (1024 * 1024):.1f} MB")
        else:
            self.stat_size.set_value(f"{self._total_bytes / 1024:.0f} KB")

        if self._assets_total > 0:
            self.progress.setRange(0, self._assets_total)
            self.progress.setValue(self._assets_done)
            pct = int(self._assets_done * 100 / self._assets_total)
            self.progress.setFormat(
                f"İndiriliyor: {self._assets_done}/{self._assets_total} dosya (%{pct})"
            )

    def _on_clone_finished(self, result: CloneResult, zip_path: str) -> None:
        self._timer.stop()
        self._worker = None
        self._last_result = result
        self._last_zip = zip_path
        self.stat_time.set_value(f"{result.elapsed:.1f} sn")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setRange(0, 100)

        if result.cancelled:
            self.progress.setValue(0)
            self.progress.setFormat("İşlem İptal Edildi")
            self.status_pill.setText("İPTAL EDİLDİ")
            self.status_pill.setStyleSheet("background-color: #7f1d1d; color: #ffffff;")
            self._log("\n⏹ İşlem kullanıcı tarafından iptal edildi.")
            self._refresh_action_buttons()
            return

        if not result.pages:
            self.progress.setValue(0)
            self.progress.setFormat("Başarısız — Ana sayfa indirilemedi")
            self.status_pill.setText("BAŞARISIZ")
            self.status_pill.setStyleSheet("background-color: #991b1b; color: #ffffff;")
            self._log("\n❌ Klonlama başarısız oldu: Ana sayfa indirilemedi.")
            self._refresh_action_buttons()
            return

        self.progress.setValue(100)
        total_mb = result.total_bytes / (1024 * 1024)
        self.progress.setFormat(
            f"Tamamlandı! {len(result.pages)} sayfa, {result.assets_ok} dosya ({total_mb:.1f} MB - {result.elapsed:.1f} sn)"
        )
        self.status_pill.setText("TAMAMLANDI")
        self.status_pill.setStyleSheet("background-color: #065f46; color: #34d399; border-color: #10b981;")

        self._log("\n" + "=" * 65)
        self._log(f"✅ KLONLAMA TAMAMLANDI ({result.elapsed:.1f} saniye | {total_mb:.2f} MB)")
        self._log(f"   • Sayfa sayısı : {len(result.pages)}")
        self._log(f"   • Dosya sayısı : {result.assets_ok}")
        self._log(f"   • Hatalı       : {len(result.failed)}")
        self._log(f"   • Klasör       : {result.output_dir.resolve()}")
        if result.index_file:
            self._log(f"   • Ana dosya    : {result.index_file.resolve()}")
        if result.recon_html:
            self._log(f"   • İstihbarat   : {result.recon_html.resolve()}")
        if zip_path:
            self._log(f"   • ZIP Arşivi   : {zip_path}")
        self._log("=" * 65)

        self.open_folder_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.open_html_btn.setEnabled(bool(result.index_file and result.index_file.exists()))
        self.open_recon_btn.setEnabled(bool(result.recon_html and result.recon_html.exists()))
        self.open_html_report_btn.setEnabled(bool(result.recon_html and result.recon_html.exists()))

    # ------------------------------------------------------------ Aksiyonlar
    def _target_dir(self) -> Path | None:
        if self._last_result and self._last_result.output_dir.is_dir():
            return self._last_result.output_dir.resolve()
        d = self._current_out_dir()
        return d.resolve() if d.is_dir() else None

    def _target_index(self) -> Path | None:
        if self._last_result and self._last_result.index_file and self._last_result.index_file.is_file():
            return self._last_result.index_file.resolve()
        d = self._target_dir()
        if d and (d / "index.html").is_file():
            return (d / "index.html").resolve()
        return None

    def _open_folder(self) -> None:
        d = self._target_dir()
        if d:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))

    def _open_index_html(self) -> None:
        idx = self._target_index()
        if idx:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(idx)))

    def _open_recon_report(self) -> None:
        d = self._target_dir()
        if d:
            html_rep = d / "recon_report.html"
            if html_rep.is_file():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(html_rep)))

    def _open_preview(self) -> None:
        d = self._target_dir()
        if not d:
            return
        base_url = self._preview.serve(d)
        rel = "index.html"
        idx = self._target_index()
        if idx:
            rel = idx.relative_to(d).as_posix()
        full_url = f"{base_url}/{rel}"
        self._log(f"🌐 Canlı önizleme sunucusu açıldı: {full_url}")
        webbrowser.open(full_url)

    def closeEvent(self, event) -> None:  # noqa: N802
        self._preview.stop()
        super().closeEvent(event)


def launch_gui(initial_url: str = "") -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("WebClone")
    win = MainWindow(initial_url=initial_url)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch_gui())
