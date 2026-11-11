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
from .i18n import LANGUAGES, get_current_language, set_language, t
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

    def set_label(self, text: str) -> None:
        self.lbl.setText(text)


class MainWindow(QMainWindow):
    def __init__(self, initial_url: str = "") -> None:
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.setWindowIcon(_make_app_icon())
        self.resize(1020, 760)
        self.setStyleSheet(STYLESHEET)

        self._current_state = "ready"
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

        # Dil Seçici (Language Switcher)
        self.lang_combo = QComboBox()
        for code, name in LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        cur_lang = get_current_language()
        for idx in range(self.lang_combo.count()):
            if self.lang_combo.itemData(idx) == cur_lang:
                self.lang_combo.setCurrentIndex(idx)
                break
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        header.addWidget(self.lang_combo)

        self.status_pill = QLabel(t("ready"))
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
        self.url_edit.setPlaceholderText(t("url_placeholder"))
        self.url_edit.textChanged.connect(self._on_url_changed)
        self.url_edit.returnPressed.connect(self._start_clone)

        self.paste_btn = QPushButton(t("paste"))
        self.paste_btn.clicked.connect(self._paste_url)

        self.start_btn = QPushButton(t("start"))
        self.start_btn.setObjectName("primaryBtn")
        self.start_btn.clicked.connect(self._start_clone)

        self.stop_btn = QPushButton(t("stop"))
        self.stop_btn.setObjectName("dangerBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_clone)

        url_row.addWidget(self.url_edit, 1)
        url_row.addWidget(self.paste_btn)
        url_row.addWidget(self.start_btn)
        url_row.addWidget(self.stop_btn)
        hero_lay.addLayout(url_row)

        # Çıktı Klasörü
        out_row = QHBoxLayout()
        self.out_lbl = QLabel(t("output_dir"))
        self.out_lbl.setStyleSheet("font-weight: 600; color: #94a3b8;")
        self.out_edit = QLineEdit()
        self.out_edit.textEdited.connect(self._on_output_edited)
        self.out_edit.textChanged.connect(self._refresh_action_buttons)
        self.browse_btn = QPushButton(t("browse"))
        self.browse_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self.out_lbl)
        out_row.addWidget(self.out_edit, 1)
        out_row.addWidget(self.browse_btn)
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
        self.stat_pages = StatBox(t("stat_pages"), "0")
        self.stat_assets = StatBox(t("stat_assets"), "0 / 0")
        self.stat_size = StatBox(t("stat_size"), "0 KB")
        self.stat_time = StatBox(t("stat_time"), "0.0 sn")
        self.stat_errors = StatBox(t("stat_errors"), "0")
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
        self.progress.setFormat(t("ready"))
        dash_lay.addWidget(self.progress)

        # Hızlı Aksiyon Butonları
        actions = QHBoxLayout()
        self.open_folder_btn = QPushButton(t("open_folder"))
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_folder)

        self.preview_btn = QPushButton(t("preview"))
        self.preview_btn.setObjectName("successBtn")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._open_preview)

        self.open_html_btn = QPushButton(t("open_html"))
        self.open_html_btn.setEnabled(False)
        self.open_html_btn.clicked.connect(self._open_index_html)

        self.open_recon_btn = QPushButton(t("open_recon"))
        self.open_recon_btn.setEnabled(False)
        self.open_recon_btn.clicked.connect(self._open_recon_report)

        actions.addWidget(self.open_folder_btn)
        actions.addWidget(self.preview_btn)
        actions.addWidget(self.open_html_btn)
        actions.addWidget(self.open_recon_btn)
        actions.addStretch()
        dash_lay.addLayout(actions)

        # Canlı mini akış
        self.dash_log_lbl = QLabel(t("live_flow"))
        self.dash_log_lbl.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 11px;")
        dash_lay.addWidget(self.dash_log_lbl)
        self.dash_log = QPlainTextEdit()
        self.dash_log.setReadOnly(True)
        self.dash_log.setMaximumBlockCount(1000)
        self.dash_log.setPlaceholderText(t("flow_placeholder"))
        dash_lay.addWidget(self.dash_log, 1)

        self.tabs.addTab(tab_dashboard, t("tab_dashboard"))

        # TAB 2: Klonlama Ayarları
        tab_settings = QWidget()
        set_lay = QVBoxLayout(tab_settings)
        set_lay.setContentsMargins(14, 14, 14, 14)
        set_lay.setSpacing(12)

        set_grid = QGridLayout()
        set_grid.setHorizontalSpacing(16)
        set_grid.setVerticalSpacing(10)

        self.lbl_depth = QLabel(t("depth"))
        set_grid.addWidget(self.lbl_depth, 0, 0)
        self.depth_combo = QComboBox()
        self.depth_combo.addItem(t("depth_0"), 0)
        self.depth_combo.addItem(t("depth_1"), 1)
        self.depth_combo.addItem(t("depth_2"), 2)
        self.depth_combo.addItem(t("depth_3"), 3)
        self.depth_combo.setCurrentIndex(1)
        set_grid.addWidget(self.depth_combo, 0, 1)

        self.lbl_layout = QLabel(t("layout"))
        set_grid.addWidget(self.lbl_layout, 0, 2)
        self.layout_combo = QComboBox()
        self.layout_combo.addItem(t("layout_org"), "organized")
        self.layout_combo.addItem(t("layout_mir"), "mirror")
        set_grid.addWidget(self.layout_combo, 0, 3)

        self.lbl_max_pages = QLabel(t("max_pages"))
        set_grid.addWidget(self.lbl_max_pages, 1, 0)
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 5000)
        self.max_pages_spin.setValue(50)
        set_grid.addWidget(self.max_pages_spin, 1, 1)

        self.lbl_workers = QLabel(t("workers"))
        set_grid.addWidget(self.lbl_workers, 1, 2)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 64)
        self.workers_spin.setValue(16)
        set_grid.addWidget(self.workers_spin, 1, 3)

        self.lbl_timeout = QLabel(t("timeout"))
        set_grid.addWidget(self.lbl_timeout, 2, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(3, 60)
        self.timeout_spin.setValue(12)
        set_grid.addWidget(self.timeout_spin, 2, 1)
        set_lay.addLayout(set_grid)

        # Filtreleme Grubu
        self.filter_group = QGroupBox(t("asset_types"))
        filter_lay = QGridLayout(self.filter_group)
        self.chk_images = QCheckBox(t("chk_images"))
        self.chk_images.setChecked(True)
        self.chk_styles = QCheckBox(t("chk_styles"))
        self.chk_styles.setChecked(True)
        self.chk_scripts = QCheckBox(t("chk_scripts"))
        self.chk_scripts.setChecked(True)
        self.chk_fonts = QCheckBox(t("chk_fonts"))
        self.chk_fonts.setChecked(True)
        self.chk_media = QCheckBox(t("chk_media"))
        self.chk_media.setChecked(True)
        self.chk_docs = QCheckBox(t("chk_docs"))
        self.chk_docs.setChecked(True)

        filter_lay.addWidget(self.chk_images, 0, 0)
        filter_lay.addWidget(self.chk_styles, 0, 1)
        filter_lay.addWidget(self.chk_scripts, 1, 0)
        filter_lay.addWidget(self.chk_fonts, 1, 1)
        filter_lay.addWidget(self.chk_media, 2, 0)
        filter_lay.addWidget(self.chk_docs, 2, 1)
        set_lay.addWidget(self.filter_group)

        # Diğer Seçenekler
        self.extra_group = QGroupBox(t("general_opts"))
        extra_lay = QVBoxLayout(self.extra_group)
        self.ext_check = QCheckBox(t("chk_external"))
        self.ext_check.setChecked(True)
        self.render_js_check = QCheckBox(t("chk_render_js"))
        self.zip_check = QCheckBox(t("chk_zip"))
        self.zip_check.setChecked(True)
        self.recon_check = QCheckBox(t("chk_recon"))
        self.recon_check.setChecked(True)
        extra_lay.addWidget(self.ext_check)
        extra_lay.addWidget(self.render_js_check)
        extra_lay.addWidget(self.zip_check)
        extra_lay.addWidget(self.recon_check)
        set_lay.addWidget(self.extra_group)
        set_lay.addStretch()

        self.tabs.addTab(tab_settings, t("tab_settings"))

        # TAB 3: Gizlilik & Anonimlik (Stealth)
        tab_stealth = QWidget()
        stealth_lay = QVBoxLayout(tab_stealth)
        stealth_lay.setContentsMargins(14, 14, 14, 14)
        stealth_lay.setSpacing(14)

        self.ua_group = QGroupBox(t("ua_group"))
        ua_lay = QGridLayout(self.ua_group)
        self.lbl_profile = QLabel(t("browser_profile"))
        ua_lay.addWidget(self.lbl_profile, 0, 0)
        self.ua_combo = QComboBox()
        self.ua_combo.addItem(t("ua_random"), "random")
        for prof in PROFILES:
            self.ua_combo.addItem(f"💻 {prof.name}", prof.name)
        ua_lay.addWidget(self.ua_combo, 0, 1)

        self.rotate_ua_check = QCheckBox(t("chk_rotate_ua"))
        self.rotate_ua_check.setChecked(True)
        ua_lay.addWidget(self.rotate_ua_check, 1, 0, 1, 2)
        stealth_lay.addWidget(self.ua_group)

        # Referer & Ağ Kamuflajı
        self.cam_group = QGroupBox(t("cam_group"))
        cam_lay = QGridLayout(self.cam_group)
        self.lbl_referer = QLabel(t("referer"))
        cam_lay.addWidget(self.lbl_referer, 0, 0)
        self.referer_combo = QComboBox()
        self.referer_combo.addItem(t("ref_google"), "google")
        self.referer_combo.addItem(t("ref_duck"), "duckduckgo")
        self.referer_combo.addItem(t("ref_bing"), "bing")
        self.referer_combo.addItem(t("ref_self"), "self")
        self.referer_combo.addItem(t("ref_none"), "none")
        cam_lay.addWidget(self.referer_combo, 0, 1)

        self.lbl_jitter = QLabel(t("jitter"))
        cam_lay.addWidget(self.lbl_jitter, 1, 0)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 5.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setValue(0.0)
        cam_lay.addWidget(self.delay_spin, 1, 1)
        stealth_lay.addWidget(self.cam_group)

        # Proxy Grubu
        self.proxy_group = QGroupBox(t("proxy_group"))
        proxy_lay = QGridLayout(self.proxy_group)
        self.lbl_proxy = QLabel(t("proxy_addr"))
        proxy_lay.addWidget(self.lbl_proxy, 0, 0)
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText(t("proxy_placeholder"))
        proxy_lay.addWidget(self.proxy_edit, 0, 1)

        self.test_proxy_btn = QPushButton(t("test_proxy"))
        self.test_proxy_btn.clicked.connect(self._test_proxy)
        proxy_lay.addWidget(self.test_proxy_btn, 0, 2)

        self.proxy_status_lbl = QLabel(t("proxy_info"))
        self.proxy_status_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        proxy_lay.addWidget(self.proxy_status_lbl, 1, 0, 1, 3)
        stealth_lay.addWidget(self.proxy_group)
        stealth_lay.addStretch()

        self.tabs.addTab(tab_stealth, t("tab_stealth"))

        # TAB 4: Hedef İstihbarat & Bilgi Toplama (Recon)
        tab_recon = QWidget()
        recon_lay = QVBoxLayout(tab_recon)
        recon_lay.setContentsMargins(14, 14, 14, 14)
        recon_lay.setSpacing(12)

        self.recon_view = QPlainTextEdit()
        self.recon_view.setReadOnly(True)
        self.recon_view.setPlaceholderText(t("recon_placeholder"))
        recon_lay.addWidget(self.recon_view, 1)

        recon_btns = QHBoxLayout()
        self.open_html_report_btn = QPushButton(t("open_html_report"))
        self.open_html_report_btn.setObjectName("successBtn")
        self.open_html_report_btn.setEnabled(False)
        self.open_html_report_btn.clicked.connect(self._open_recon_report)
        recon_btns.addWidget(self.open_html_report_btn)
        recon_btns.addStretch()
        recon_lay.addLayout(recon_btns)

        self.tabs.addTab(tab_recon, t("tab_recon"))

        # TAB 5: Ayrıntılı Canlı Günlük (Live Console)
        tab_log = QWidget()
        log_lay = QVBoxLayout(tab_log)
        log_lay.setContentsMargins(14, 14, 14, 14)
        log_lay.setSpacing(10)

        log_tools = QHBoxLayout()
        self.log_filter = QLineEdit()
        self.log_filter.setPlaceholderText(t("filter_placeholder"))
        self.clear_btn = QPushButton(t("clear"))
        self.clear_btn.clicked.connect(self._clear_logs)
        log_tools.addWidget(self.log_filter, 1)
        log_tools.addWidget(self.clear_btn)
        log_lay.addLayout(log_tools)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(3000)
        log_lay.addWidget(self.log_box, 1)

        self.tabs.addTab(tab_log, t("tab_console"))

        root.addWidget(self.tabs, 1)

    def _on_lang_changed(self, index: int) -> None:
        lang_code = self.lang_combo.itemData(index)
        set_language(lang_code)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(t("app_title"))
        self.url_edit.setPlaceholderText(t("url_placeholder"))
        self.paste_btn.setText(t("paste"))
        self.start_btn.setText(t("start"))
        self.stop_btn.setText(t("stop"))
        self.out_lbl.setText(t("output_dir"))
        self.browse_btn.setText(t("browse"))

        # Status pill
        status_map = {
            "ready": t("ready"),
            "connecting": t("connecting"),
            "cloning": t("cloning"),
            "completed": t("completed"),
            "cancelled": t("cancelled"),
            "failed": t("failed"),
            "stopping": t("stopping"),
        }
        self.status_pill.setText(status_map.get(self._current_state, t("ready")))

        # Tabs
        self.tabs.setTabText(0, t("tab_dashboard"))
        self.tabs.setTabText(1, t("tab_settings"))
        self.tabs.setTabText(2, t("tab_stealth"))
        self.tabs.setTabText(3, t("tab_recon"))
        self.tabs.setTabText(4, t("tab_console"))

        # Stats
        self.stat_pages.set_label(t("stat_pages"))
        self.stat_assets.set_label(t("stat_assets"))
        self.stat_size.set_label(t("stat_size"))
        self.stat_time.set_label(t("stat_time"))
        self.stat_errors.set_label(t("stat_errors"))

        # Actions
        self.open_folder_btn.setText(t("open_folder"))
        self.preview_btn.setText(t("preview"))
        self.open_html_btn.setText(t("open_html"))
        self.open_recon_btn.setText(t("open_recon"))
        self.dash_log_lbl.setText(t("live_flow"))
        self.dash_log.setPlaceholderText(t("flow_placeholder"))

        # Settings
        self.lbl_depth.setText(t("depth"))
        self.depth_combo.setItemText(0, t("depth_0"))
        self.depth_combo.setItemText(1, t("depth_1"))
        self.depth_combo.setItemText(2, t("depth_2"))
        self.depth_combo.setItemText(3, t("depth_3"))

        self.lbl_layout.setText(t("layout"))
        self.layout_combo.setItemText(0, t("layout_org"))
        self.layout_combo.setItemText(1, t("layout_mir"))

        self.lbl_max_pages.setText(t("max_pages"))
        self.lbl_workers.setText(t("workers"))
        self.lbl_timeout.setText(t("timeout"))

        self.filter_group.setTitle(t("asset_types"))
        self.chk_images.setText(t("chk_images"))
        self.chk_styles.setText(t("chk_styles"))
        self.chk_scripts.setText(t("chk_scripts"))
        self.chk_fonts.setText(t("chk_fonts"))
        self.chk_media.setText(t("chk_media"))
        self.chk_docs.setText(t("chk_docs"))

        self.extra_group.setTitle(t("general_opts"))
        self.ext_check.setText(t("chk_external"))
        self.render_js_check.setText(t("chk_render_js"))
        self.zip_check.setText(t("chk_zip"))
        self.recon_check.setText(t("chk_recon"))

        # Stealth
        self.ua_group.setTitle(t("ua_group"))
        self.lbl_profile.setText(t("browser_profile"))
        self.ua_combo.setItemText(0, t("ua_random"))
        self.rotate_ua_check.setText(t("chk_rotate_ua"))

        self.cam_group.setTitle(t("cam_group"))
        self.lbl_referer.setText(t("referer"))
        self.referer_combo.setItemText(0, t("ref_google"))
        self.referer_combo.setItemText(1, t("ref_duck"))
        self.referer_combo.setItemText(2, t("ref_bing"))
        self.referer_combo.setItemText(3, t("ref_self"))
        self.referer_combo.setItemText(4, t("ref_none"))
        self.lbl_jitter.setText(t("jitter"))

        self.proxy_group.setTitle(t("proxy_group"))
        self.lbl_proxy.setText(t("proxy_addr"))
        self.proxy_edit.setPlaceholderText(t("proxy_placeholder"))
        self.test_proxy_btn.setText(t("test_proxy"))
        self.proxy_status_lbl.setText(t("proxy_info"))

        # Recon & Log
        self.recon_view.setPlaceholderText(t("recon_placeholder"))
        self.open_html_report_btn.setText(t("open_html_report"))
        self.log_filter.setPlaceholderText(t("filter_placeholder"))
        self.clear_btn.setText(t("clear"))

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
        folder = QFileDialog.getExistingDirectory(self, t("output_dir"), self.out_edit.text())
        if folder:
            self._custom_out = True
            self.out_edit.setText(folder)

    def _log(self, msg: str) -> None:
        self.dash_log.appendPlainText(msg)
        self.log_box.appendPlainText(msg)

    def _clear_logs(self) -> None:
        self.dash_log.clear()
        self.log_box.clear()

    def _tick_timer(self) -> None:
        elapsed = time.monotonic() - self._t0
        self.stat_time.set_value(f"{elapsed:.1f} s")

    def _test_proxy(self) -> None:
        proxy = self.proxy_edit.text().strip()
        if not proxy:
            QMessageBox.information(self, t("info_title"), t("enter_proxy_first"))
            return

        self.proxy_status_lbl.setText("🔄 ...")
        self.test_proxy_btn.setEnabled(False)

        def run_test():
            res = StealthManager.test_proxy(proxy)
            QTimer.singleShot(0, lambda: self._on_proxy_tested(res))

        threading.Thread(target=run_test, daemon=True).start()

    def _on_proxy_tested(self, res: dict) -> None:
        self.test_proxy_btn.setEnabled(True)
        if res["ok"]:
            self.proxy_status_lbl.setText(
                f"✅ IP: {res['ip']}  ({res['latency']} ms)"
            )
            self.proxy_status_lbl.setStyleSheet("color: #34d399; font-weight: 600; font-size: 11px;")
        else:
            self.proxy_status_lbl.setText(f"❌ {res['error']}")
            self.proxy_status_lbl.setStyleSheet("color: #f87171; font-weight: 600; font-size: 11px;")

    # ------------------------------------------------------------ Klonlama
    def _start_clone(self) -> None:
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, t("warning_title"), t("warning_empty_url"))
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
        self.stat_time.set_value("0.0 s")
        self.progress.setRange(0, 0)
        self.progress.setFormat(t("connecting"))
        self._current_state = "connecting"
        self.status_pill.setText(t("connecting"))
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
            self._log("⏹ ...")
            self.stop_btn.setEnabled(False)
            self._current_state = "stopping"
            self.status_pill.setText(t("stopping"))

    def _on_clone_event(self, name: str, data: dict) -> None:
        if name == "start":
            self._current_state = "cloning"
            self.status_pill.setText(t("cloning"))
            self._log(f"🚀 {t('cloning')}: {data['url']}")
            self._log(f"📁 {t('output_dir')} {data['output_dir']}\n")
        elif name == "recon_done":
            rep: ReconReport = data.get("report")
            if rep:
                self._update_recon_ui(rep)
        elif name == "page_start":
            self._log(f"📄 [PAGE] {data['url']}  →  {data['path']}")
        elif name == "page_done":
            self._pages_count += 1
            self.stat_pages.set_value(str(self._pages_count))
        elif name == "page_failed":
            self._errors_count += 1
            self.stat_errors.set_value(str(self._errors_count))
            self._log(f"❌ [PAGE ERROR] {data['url']} — {data['error']}")
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
            self._log(f"  ⚠ [ASSET ERROR] {data['url']} — {data['error']}")

    def _update_recon_ui(self, rep: ReconReport) -> None:
        techs = ", ".join(t["name"] for t in rep.technologies) or "N/A"
        text = f"""🔍 TARGET RECONNAISSANCE REPORT
==================================================
• Target URL    : {rep.target_url}
• Hostname      : {rep.hostname}
• IP Address    : {rep.ip_address}
• Web Server    : {rep.server}
• Backend/Power : {rep.powered_by or 'Hidden'}
• Page Title    : {rep.meta_title or 'N/A'}
• Language      : {rep.language or 'N/A'}
• Technologies  : {techs}
• robots.txt    : {'Found' if rep.robots_found else 'N/A'}
==================================================
Security Headers:
"""
        for s in rep.security_headers:
            status = "✅ Active" if s["present"] else "❌ Missing"
            text += f"  [{status}] {s['title']} ({s['header']})\n"
        self.recon_view.setPlainText(text)

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
                f"{self._assets_done}/{self._assets_total} (%{pct})"
            )

    def _on_clone_finished(self, result: CloneResult, zip_path: str) -> None:
        self._timer.stop()
        self._worker = None
        self._last_result = result
        self._last_zip = zip_path
        self.stat_time.set_value(f"{result.elapsed:.1f} s")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setRange(0, 100)

        if result.cancelled:
            self.progress.setValue(0)
            self.progress.setFormat(t("cancelled"))
            self._current_state = "cancelled"
            self.status_pill.setText(t("cancelled"))
            self.status_pill.setStyleSheet("background-color: #7f1d1d; color: #ffffff;")
            self._log("\n⏹ " + t("cancelled"))
            self._refresh_action_buttons()
            return

        if not result.pages:
            self.progress.setValue(0)
            self.progress.setFormat(t("failed"))
            self._current_state = "failed"
            self.status_pill.setText(t("failed"))
            self.status_pill.setStyleSheet("background-color: #991b1b; color: #ffffff;")
            self._log("\n❌ " + t("failed"))
            self._refresh_action_buttons()
            return

        self.progress.setValue(100)
        total_mb = result.total_bytes / (1024 * 1024)
        self.progress.setFormat(
            f"{t('completed')} — {len(result.pages)} p., {result.assets_ok} files ({total_mb:.1f} MB | {result.elapsed:.1f} s)"
        )
        self._current_state = "completed"
        self.status_pill.setText(t("completed"))
        self.status_pill.setStyleSheet("background-color: #065f46; color: #34d399; border-color: #10b981;")

        self._log("\n" + "=" * 65)
        self._log(f"✅ {t('completed')} ({result.elapsed:.1f} s | {total_mb:.2f} MB)")
        self._log(f"   • Pages        : {len(result.pages)}")
        self._log(f"   • Assets       : {result.assets_ok}")
        self._log(f"   • Failed       : {len(result.failed)}")
        self._log(f"   • Folder       : {result.output_dir.resolve()}")
        if result.index_file:
            self._log(f"   • Index        : {result.index_file.resolve()}")
        if result.recon_html:
            self._log(f"   • Recon Report : {result.recon_html.resolve()}")
        if zip_path:
            self._log(f"   • ZIP Archive  : {zip_path}")
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
        self._log(f"🌐 Server: {full_url}")
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
