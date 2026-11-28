import os
import sys
import json
import time
import queue
import subprocess
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QSpinBox, QSystemTrayIcon, QMenu, QAction, QFileDialog, QMessageBox,
    QFrame, QGridLayout, QFormLayout, QScrollArea, QProgressBar, QSplashScreen, QInputDialog,
    QDialog, QStackedWidget, QListWidget, QListWidgetItem
)

from config import (
    APP_NAME, APP_DATA_DIR, SETTINGS_FILE, PRESETS_FILE,
    SESSION_HISTORY_FILE, SESSION_LOG_FILE, SCRCPY_EXECUTABLE,
    SCRCPY_DIRECTORY, QTSCRCPY_EXECUTABLE, UXPLAY_EXECUTABLE, UXPLAY_DIRECTORY
)
from android_engine import AndroidManager
from ios_engine import IOSManager


# -----------------------------------------------------------------------------
# DARK GLASSMORPHISM STYLESHEET (KEEPING THE ULTRA-PREMIUM COLOR SCHEME)
# -----------------------------------------------------------------------------
GLASS_DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #111827;
    color: #f8fafc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#headerFrame {
    background-color: #111827;
    border-bottom: 1px solid #263244;
}
QFrame#cardFrame {
    background-color: #182230;
    border: 1px solid #263244;
    border-radius: 12px;
}
QFrame#toolbarFrame {
    background-color: #111827;
    border: 1px solid #263244;
    border-radius: 8px;
}

QListWidget#navRail {
    background-color: #0d1521;
    border: none;
    border-right: 1px solid #263244;
    outline: none;
    padding: 12px 8px;
}
QListWidget#navRail::item {
    color: #94a3b8;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 2px 0;
}
QListWidget#navRail::item:selected {
    background-color: #172a3a;
    color: #38bdf8;
}
QListWidget#navRail::item:hover:!selected {
    background-color: #182230;
    color: #e2e8f0;
}

QGroupBox {
    border: 1px solid #263244;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #cbd5e1;
    background-color: #182230;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
}

QPushButton {
    background-color: #263244;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 14px;
    min-height: 22px;
    font-weight: 600;
}
QPushButton:hover { background-color: #334155; border-color: #475569; }
QPushButton:pressed { background-color: #1e293b; }
QPushButton:focus { border: 2px solid #38bdf8; }
QPushButton:disabled { color: #64748b; background-color: #1e293b; border-color: #263244; }
QPushButton#successBtn { background-color: #087f5b; color: #ffffff; border-color: #10b981; }
QPushButton#successBtn:hover { background-color: #099268; }
QPushButton#dangerBtn { background-color: #8f2d3b; color: #ffffff; border-color: #b94a5a; }
QPushButton#dangerBtn:hover { background-color: #a83b49; }
QPushButton#purpleBtn { background-color: #6550a3; color: #ffffff; border-color: #8065c6; }
QPushButton#purpleBtn:hover { background-color: #735bb5; }
QPushButton#toolBtn {
    background-color: #182230;
    color: #cbd5e1;
    border: 1px solid #263244;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
    font-size: 12px;
}
QPushButton#toolBtn:hover { color: #38bdf8; border-color: #38bdf8; }

QLineEdit, QComboBox, QSpinBox {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 10px;
    min-height: 22px;
    color: #f8fafc;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #38bdf8; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #182230;
    selection-background-color: #172a3a;
    selection-color: #38bdf8;
    border: 1px solid #334155;
}

QCheckBox { spacing: 8px; color: #e2e8f0; }
QCheckBox::indicator {
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1px solid #475569;
    background-color: #111827;
}
QCheckBox::indicator:checked { background-color: #38bdf8; border-color: #38bdf8; }

QTableWidget {
    background-color: #182230;
    alternate-background-color: #16202d;
    border: 1px solid #263244;
    border-radius: 8px;
    gridline-color: #263244;
}
QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #263244;
    font-weight: 600;
}
QTextEdit {
    background-color: #0d1521;
    border: 1px solid #263244;
    border-radius: 8px;
    color: #e2e8f0;
    font-family: 'Consolas', 'Courier New', monospace;
}
QScrollArea { border: none; background: transparent; }
"""


# -----------------------------------------------------------------------------
# SPLASH SCREEN BOOT ANIMATION
# -----------------------------------------------------------------------------
class MorppySplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(520, 340)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #12181b;
                border: 2px solid #38bdf8;
                border-radius: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("MORPPY SUITE", card)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #38bdf8; border: none;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Next-Gen Mobile Mirroring & Control System", card)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #94a3b8; border: none;")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(16)

        # Percentage label positioned directly ABOVE the progress bar
        self.percent_lbl = QLabel("0%", card)
        self.percent_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.percent_lbl.setStyleSheet("color: #38bdf8; border: none;")
        self.percent_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.percent_lbl)

        # Progress bar (Text inside bar disabled)
        self.progress = QProgressBar(card)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1a2327;
                border-radius: 6px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #8b5cf6);
                border-radius: 6px;
            }
        """)
        card_layout.addWidget(self.progress)

        self.status_lbl = QLabel("Initializing Morppy Core Engines...", card)
        self.status_lbl.setFont(QFont("Segoe UI", 9))
        self.status_lbl.setStyleSheet("color: #cbd5e1; border: none;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.status_lbl)

        layout.addWidget(card)
    def set_progress(self, val, msg):
        self.progress.setValue(val)
        self.percent_lbl.setText(f"{val}%")
        self.status_lbl.setText(msg)
        QApplication.processEvents()


# -----------------------------------------------------------------------------
# DISPLAY SETTINGS MODAL DIALOG
# -----------------------------------------------------------------------------
class DisplaySettingsDialog(QDialog):
    def __init__(self, main_win, serial=None, is_launch=True, parent=None):
        super().__init__(parent or main_win)
        self.main_win = main_win
        self.serial = serial
        self.is_launch = is_launch

        title = f"Configure & Launch Mirroring ({serial})" if serial else "Display & Stream Settings"
        self.setWindowTitle(title)
        self.setMinimumSize(620, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #12181b;
                border: 2px solid #38bdf8;
                border-radius: 16px;
            }
            QLabel {
                background: transparent;
                font-size: 14px;
                font-weight: 600;
                color: #e2e8f0;
            }
            QFrame#dispCardRes, QFrame#dispCardAdv {
                background-color: rgba(26, 35, 39, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 12px;
            }
            QComboBox, QLineEdit {
                font-size: 13px;
                font-weight: 500;
                padding: 4px 10px;
                border-radius: 6px;
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #334155;
                min-height: 32px;
                max-height: 32px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #0284c7;
                selection-color: #ffffff;
                border: 1px solid #334155;
            }
            QCheckBox {
                background: transparent;
                font-size: 14px;
                font-weight: 500;
                color: #f8fafc;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 6px;
                min-height: 32px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(16)

        header_lbl = QLabel(f"Configure Session Display Settings ({serial})" if serial else "Display & Stream Settings")
        header_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_lbl.setStyleSheet("color: #38bdf8; margin-bottom: 2px; background: transparent;")
        layout.addWidget(header_lbl)

        # Card 1: Mirror Engine & Stream Resolution (QFormLayout)
        card_res = QFrame()
        card_res.setObjectName("dispCardRes")
        res_form = QFormLayout(card_res)
        res_form.setContentsMargins(20, 18, 20, 18)
        res_form.setHorizontalSpacing(16)
        res_form.setVerticalSpacing(16)
        res_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        sec1_title = QLabel("Mirror Engine & Stream Resolution")
        sec1_title.setStyleSheet("color: #38bdf8; font-size: 15px; font-weight: bold; margin-bottom: 6px; background: transparent;")
        res_form.addRow(sec1_title)

        # Row 1: Engine
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["scrcpy 4.0 (Default)", "QtScrcpy (Gaming Engine)"])
        self.combo_engine.setCurrentText(main_win.display_settings.get("engine", "scrcpy 4.0 (Default)"))
        self.combo_engine.setToolTip(
            "• What it does: Chooses the underlying mirror stream engine.\n"
            "• BEST CHOICE: 'scrcpy 4.0 (Default)' — Highest stability, sharpest video quality, and lowest latency.\n"
            "• ALTERNATIVE: 'QtScrcpy (Gaming Engine)' — Choose if playing fast competitive mobile games requiring keyboard keymapping."
        )
        res_form.addRow("Primary Mirror Engine:", self.combo_engine)

        # Row 2: Resolution
        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems([
            "Default (Native)",
            "1080p (Downscale)",
            "720p (Downscale)",
            "480p (Downscale)",
            "1440p (2K Hardware Upscale)",
            "2160p (4K Hardware Upscale)"
        ])
        self.combo_resolution.setCurrentText(main_win.display_settings.get("resolution", "Default (Native)"))
        self.combo_resolution.setToolTip(
            "• What it does: Controls video stream resolution and GPU scaling.\n"
            "• BEST CHOICE: 'Default (Native)' — Matches your phone screen 1:1 for 100% pixel sharpness.\n"
            "• ALTERNATIVE: '1080p' / '720p' — Saves network bandwidth on slow Wi-Fi.\n"
            "• ALTERNATIVE: '1440p' / '2160p' — Upscales output on 2K/4K PC monitors."
        )
        res_form.addRow("Stream & GPU Resolution:", self.combo_resolution)

        # Row 3: Window Size
        self.combo_window_size = QComboBox()
        self.combo_window_size.addItems(["Default", "Small", "Medium", "Large"])
        self.combo_window_size.setCurrentText(main_win.display_settings.get("window_size", "Default"))
        self.combo_window_size.setToolTip(
            "• What it does: Sets initial size of the mirror window on PC.\n"
            "• BEST CHOICE: 'Default' — Automatically fits your phone's native aspect ratio.\n"
            "• ALTERNATIVES: 'Small' (400x700), 'Medium' (600x950), or 'Large' (900x1400)."
        )
        res_form.addRow("Launch Window Size:", self.combo_window_size)

        # Row 4: Render Driver
        self.combo_render = QComboBox()
        self.combo_render.addItems(["default", "direct3d", "opengl", "software"])
        self.combo_render.setCurrentText(main_win.display_settings.get("render", "default"))
        self.combo_render.setToolTip(
            "• What it does: Specifies the PC GPU rendering driver backend.\n"
            "• BEST CHOICE: 'default' — Auto-selects the fastest hardware driver for your graphics card.\n"
            "• ALTERNATIVES: 'direct3d' for Windows DirectX, 'opengl' for cross-platform GPU, or 'software' if GPU drivers fail."
        )
        res_form.addRow("GPU Render Driver:", self.combo_render)

        layout.addWidget(card_res)

        # Card 2: Advanced Options (QFormLayout)
        card_adv = QFrame()
        card_adv.setObjectName("dispCardAdv")
        adv_form = QFormLayout(card_adv)
        adv_form.setContentsMargins(20, 16, 20, 16)
        adv_form.setHorizontalSpacing(16)
        adv_form.setVerticalSpacing(14)
        adv_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        sec2_title = QLabel("📌 Advanced Display Options")
        sec2_title.setStyleSheet("color: #38bdf8; font-size: 15px; font-weight: bold; margin-bottom: 4px; background: transparent;")
        adv_form.addRow(sec2_title)

        self.chk_virtual_display = QCheckBox("Enable Virtual Display (Spawns a secondary monitor on PC, Android 13+)")
        self.chk_virtual_display.setChecked(main_win.display_settings.get("virtual_display", False))
        self.chk_virtual_display.setToolTip(
            "• What it does: Spawns an independent secondary virtual display on PC without mirroring main phone screen (Android 13+).\n"
            "• BEST CHOICE: Disabled (Unchecked) — Recommended for standard screen mirroring."
        )
        adv_form.addRow(self.chk_virtual_display)

        self.txt_crop = QLineEdit(main_win.display_settings.get("crop", ""))
        self.txt_crop.setToolTip(
            "• What it does: Crops video stream coordinates (width:height:x:y) to hide notches or navigation bars.\n"
            "• BEST CHOICE: Leave empty for full phone display, or enter e.g. '1080:1920:0:0'."
        )
        adv_form.addRow("Video Crop (bounds:x:y):", self.txt_crop)

        layout.addWidget(card_adv)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)
        btn_box.addStretch()

        if is_launch:
            btn_cancel = QPushButton("Cancel")
            btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
            btn_cancel.clicked.connect(self.reject)
            btn_box.addWidget(btn_cancel)

            btn_start = QPushButton("🚀 Start Mirroring")
            btn_start.setObjectName("successBtn")
            btn_start.setCursor(QCursor(Qt.PointingHandCursor))
            btn_start.clicked.connect(self.save_and_accept)
            btn_box.addWidget(btn_start)
        else:
            btn_save = QPushButton("Save & Close")
            btn_save.setObjectName("successBtn")
            btn_save.setCursor(QCursor(Qt.PointingHandCursor))
            btn_save.clicked.connect(self.save_and_accept)
            btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def save_and_accept(self):
        self.main_win.display_settings["engine"] = self.combo_engine.currentText()
        self.main_win.display_settings["resolution"] = self.combo_resolution.currentText()
        self.main_win.display_settings["window_size"] = self.combo_window_size.currentText()
        self.main_win.display_settings["render"] = self.combo_render.currentText()
        self.main_win.display_settings["virtual_display"] = self.chk_virtual_display.isChecked()
        self.main_win.display_settings["crop"] = self.txt_crop.text().strip()
        self.accept()


# -----------------------------------------------------------------------------
# RECORDING SETTINGS MODAL DIALOG
# -----------------------------------------------------------------------------
class RecordingSettingsDialog(QDialog):
    def __init__(self, main_win, serial=None, parent=None):
        super().__init__(parent or main_win)
        self.main_win = main_win
        self.serial = serial

        title = f"Screen Recording Settings ({serial})" if serial else "Screen Recording Settings"
        self.setWindowTitle(title)
        self.setMinimumSize(640, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #12181b;
                border: 2px solid #f97316;
                border-radius: 16px;
            }
            QLabel {
                background: transparent;
                font-size: 14px;
                font-weight: 600;
                color: #e2e8f0;
            }
            QFrame#recCardMain, QFrame#recCardOpts {
                background-color: rgba(26, 35, 39, 0.85);
                border: 1px solid rgba(249, 115, 22, 0.35);
                border-radius: 12px;
            }
            QComboBox, QLineEdit {
                font-size: 13px;
                font-weight: 500;
                padding: 4px 10px;
                border-radius: 6px;
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #334155;
                min-height: 32px;
                max-height: 32px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #ea580c;
                selection-color: #ffffff;
                border: 1px solid #334155;
            }
            QCheckBox {
                background: transparent;
                font-size: 14px;
                font-weight: 500;
                color: #f8fafc;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 6px;
                min-height: 32px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        header_lbl = QLabel(f"Screen Recording Settings ({serial})" if serial else "Screen Recording Settings")
        header_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_lbl.setStyleSheet("color: #fb923c; margin-bottom: 2px; background: transparent;")
        layout.addWidget(header_lbl)

        # Card 1: Hardware Encoder & Format Setup (QFormLayout)
        card_rec = QFrame()
        card_rec.setObjectName("recCardMain")
        rec_form = QFormLayout(card_rec)
        rec_form.setContentsMargins(20, 18, 20, 18)
        rec_form.setHorizontalSpacing(16)
        rec_form.setVerticalSpacing(16)
        rec_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        sec1_title = QLabel("Hardware Encoder & Video Format")
        sec1_title.setStyleSheet("color: #fb923c; font-size: 15px; font-weight: bold; margin-bottom: 6px; background: transparent;")
        rec_form.addRow(sec1_title)

        # Row 1: Encoder Engine
        self.combo_engine = QComboBox()
        self.combo_engine.addItems([
            "ADB Native MediaCodec (On-Device Phone GPU)",
            "Scrcpy Native Direct Capture (PC File Saver)",
            "FFmpeg PC Hardware GPU (NVIDIA NVENC / AMD / Intel)",
            "QtScrcpy High-FPS Gaming Engine (120 FPS)"
        ])
        self.combo_engine.setCurrentText(main_win.recording_settings.get("engine", "ADB Native MediaCodec (On-Device Phone GPU)"))
        self.combo_engine.setToolTip(
            "• What it does: Selects video recording capture & hardware encoder engine.\n"
            "• BEST CHOICE: 'FFmpeg PC Hardware GPU' or 'Scrcpy Native Direct Capture' — Saves video directly to PC disk with 0% phone CPU load.\n"
            "• ALTERNATIVE: 'ADB Native MediaCodec' — Encodes directly on-device using phone's hardware MediaCodec."
        )
        rec_form.addRow("Encoder Engine:", self.combo_engine)

        # Row 2: Video Format
        self.combo_format = QComboBox()
        self.combo_format.addItems(["mp4", "mkv", "avi"])
        self.combo_format.setCurrentText(main_win.recording_settings.get("format", "mp4"))
        self.combo_format.setToolTip(
            "• What it does: Specifies output video file container format.\n"
            "• BEST CHOICE: 'mp4' — Universal compatibility with all media players, Premiere, and web sharing.\n"
            "• ALTERNATIVE: 'mkv' — Progressive saving format (prevents file corruption if power cuts during recording)."
        )
        rec_form.addRow("Video Format:", self.combo_format)

        # Row 3: Hardware Codec
        self.combo_codec = QComboBox()
        self.combo_codec.addItems(["h265 (HEVC)", "h264 (AVC)", "av1"])
        self.combo_codec.setCurrentText(main_win.recording_settings.get("codec", "h265 (HEVC)"))
        self.combo_codec.setToolTip(
            "• What it does: Compression codec used to encode recorded video.\n"
            "• BEST CHOICE: 'h265 (HEVC)' — Superior video clarity with 50% smaller file sizes.\n"
            "• ALTERNATIVE: 'h264 (AVC)' — Universal playback compatibility on older PCs."
        )
        rec_form.addRow("Hardware Codec:", self.combo_codec)

        # Row 4: Save Folder
        path_box = QHBoxLayout()
        path_box.setSpacing(10)
        self.txt_path = QLineEdit(main_win.recording_settings.get("path", SCRCPY_DIRECTORY))
        self.txt_path.setToolTip(
            "• What it does: Target PC directory where video recordings are stored.\n"
            "• BEST CHOICE: Select a folder on a fast SSD. Stopping recording automatically opens this directory."
        )
        btn_browse = QPushButton("📁 Browse")
        btn_browse.setCursor(QCursor(Qt.PointingHandCursor))
        btn_browse.clicked.connect(self.browse_folder)
        path_box.addWidget(self.txt_path, 1)
        path_box.addWidget(btn_browse)

        rec_form.addRow("Save Folder:", path_box)

        layout.addWidget(card_rec)

        # Card 2: Behavior (QFormLayout)
        card_opts = QFrame()
        card_opts.setObjectName("recCardOpts")
        opts_layout = QVBoxLayout(card_opts)
        opts_layout.setContentsMargins(20, 16, 20, 16)
        opts_layout.setSpacing(10)

        sec2_title = QLabel("📌 Recording Behavior")
        sec2_title.setStyleSheet("color: #fb923c; font-size: 15px; font-weight: bold; margin-bottom: 4px; background: transparent;")
        opts_layout.addWidget(sec2_title)

        self.chk_auto_rec = QCheckBox("Record Automatically when Mirroring Starts")
        self.chk_auto_rec.setChecked(main_win.recording_settings.get("auto_record", False))
        self.chk_auto_rec.setToolTip(
            "• What it does: Automatically begins recording video the moment you click 'Launch Mirror'.\n"
            "• BEST CHOICE: Disabled (Unchecked) — Allows starting/stopping recording manually anytime using the red Rec button."
        )
        opts_layout.addWidget(self.chk_auto_rec)

        layout.addWidget(card_opts)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_start = QPushButton("Start Recording")
        btn_start.setObjectName("dangerBtn")
        btn_start.setStyleSheet("""
            QPushButton#dangerBtn {
                background-color: #ea580c;
                color: #ffffff;
                border: 1px solid #f97316;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 26px;
                min-height: 38px;
            }
            QPushButton#dangerBtn:hover {
                background-color: #c2410c;
            }
        """)
        btn_start.setCursor(QCursor(Qt.PointingHandCursor))
        btn_start.clicked.connect(self.save_and_accept)
        btn_box.addWidget(btn_start)

        layout.addLayout(btn_box)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Recording Save Folder")
        if folder:
            self.txt_path.setText(folder)

    def save_and_accept(self):
        self.main_win.recording_settings["engine"] = self.combo_engine.currentText()
        self.main_win.recording_settings["format"] = self.combo_format.currentText()
        self.main_win.recording_settings["codec"] = self.combo_codec.currentText()
        self.main_win.recording_settings["path"] = self.txt_path.text().strip()
        self.main_win.recording_settings["auto_record"] = self.chk_auto_rec.isChecked()
        self.accept()


# -----------------------------------------------------------------------------
# WORKER THREADS
# -----------------------------------------------------------------------------
class DeviceScannerWorker(QThread):
    devices_signal = pyqtSignal(list)

    def run(self):
        devices = AndroidManager.get_devices()
        self.devices_signal.emit(devices)


class TelemetryWorker(QThread):
    telemetry_signal = pyqtSignal(str, dict)

    def __init__(self, devices):
        super().__init__()
        self.devices = list(devices)

    def run(self):
        for serial in self.devices:
            telemetry = AndroidManager.get_telemetry(serial)
            self.telemetry_signal.emit(serial, telemetry)


def detect_recommended_recording_engine():
    try:
        if os.name == 'nt':
            c_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            cmd = ["powershell", "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"]
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=c_flags)
            gpus = proc.stdout.lower()
            if any(gpu_name in gpus for gpu_name in ["nvidia", "geforce", "rtx", "gtx", "radeon", "arc"]):
                return "FFmpeg PC Hardware GPU (NVIDIA NVENC / AMD / Intel)"
    except Exception:
        pass
    return "Scrcpy Native Direct Capture (PC File Saver)"


# -----------------------------------------------------------------------------
# MAIN APPLICATION WINDOW
# -----------------------------------------------------------------------------
class MorppyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morppy Mobile Mirror Suite")
        self.resize(1180, 840)

        # State storage
        self.active_sessions = {}
        self.known_devices = []
        self.ios_manager = IOSManager()
        self.session_history = self.load_session_history()
        self.presets = self.load_presets()

        # Persistent Display Settings state dictionary (prevents C++ Qt widget deletion bugs)
        self.display_settings = {
            "engine": "scrcpy 4.0 (Default)",
            "resolution": "Default (Native)",
            "window_size": "Default",
            "render": "default",
            "virtual_display": False,
            "crop": ""
        }

        # Recording sessions tracking state & blinking animation state
        self.recording_sessions = {}
        self.rec_blink_state = False

        # GPU-based Auto-Detection of Recommended Recording Engine
        recommended_rec_engine = detect_recommended_recording_engine()

        # Persistent Recording Settings state dictionary
        self.recording_settings = {
            "format": "mp4",
            "path": SCRCPY_DIRECTORY,
            "engine": recommended_rec_engine,
            "codec": "h265 (HEVC)",
            "auto_record": False
        }

        self.init_ui()
        self.init_system_tray()

        # Timers
        self.scan_timer = QTimer(self)
        self.scan_timer.setInterval(3000)
        self.scan_timer.timeout.connect(self.start_device_scan)
        self.scan_timer.start()

        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.setInterval(1000)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start()

        self.rec_blink_timer = QTimer(self)
        self.rec_blink_timer.setInterval(500)
        self.rec_blink_timer.timeout.connect(self.animate_recording_blink)
        self.rec_blink_timer.start()

        self.start_device_scan()
        self.log_message("Morppy Suite UI initialized.")

    def init_ui(self):
        self.setStyleSheet(GLASS_DARK_QSS)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)

        logo_lbl = QLabel("Morppy")
        logo_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_lbl.setStyleSheet("color: #38bdf8;")

        self.status_badge = QLabel("System Ready")
        self.status_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #34d399;
            font-weight: bold;
            padding: 6px 14px;
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 14px;
        """)

        btn_refresh = QPushButton("Refresh Devices")
        btn_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        btn_refresh.clicked.connect(self.start_device_scan)

        btn_reset_adb = QPushButton("Reset ADB")
        btn_reset_adb.setObjectName("dangerBtn")
        btn_reset_adb.setCursor(QCursor(Qt.PointingHandCursor))
        btn_reset_adb.clicked.connect(self.reset_adb_server)

        header_layout.addWidget(logo_lbl)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Preset"))
        self.quick_preset = QComboBox()
        self.quick_preset.addItems(list(self.presets.keys()))
        self.quick_preset.currentTextChanged.connect(self.apply_quick_preset)
        header_layout.addWidget(self.quick_preset)
        header_layout.addWidget(self.status_badge)
        header_layout.addWidget(btn_refresh)
        header_layout.addWidget(btn_reset_adb)

        main_layout.addWidget(header_frame)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.nav_rail = QListWidget()
        self.nav_rail.setObjectName("navRail")
        self.nav_rail.setFixedWidth(190)
        for label in ("Devices", "Global Settings", "Presets & History", "iOS AirPlay", "Logs"):
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.nav_rail.addItem(item)

        self.content_pages = QStackedWidget()
        self.nav_rail.currentRowChanged.connect(self.content_pages.setCurrentIndex)

        content_layout.addWidget(self.nav_rail)
        content_layout.addWidget(self.content_pages, 1)
        main_layout.addLayout(content_layout, 1)

        self.build_devices_tab()
        self.build_global_settings_tab()
        self.build_presets_history_tab()
        self.build_ios_tab()
        self.build_logs_tab()
        self.nav_rail.setCurrentRow(0)

    # -------------------------------------------------------------------------
    # TAB 1: DEVICES & CONNECTION
    def build_devices_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        connect_box = QGroupBox("Wireless ADB Connection")
        connect_layout = QHBoxLayout(connect_box)

        connect_layout.addWidget(QLabel("IP Address & Port:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("e.g. 192.168.1.35:5555")
        connect_layout.addWidget(self.ip_input, 1)

        btn_connect_ip = QPushButton("🔌 Connect Wireless")
        btn_connect_ip.setCursor(QCursor(Qt.PointingHandCursor))
        btn_connect_ip.clicked.connect(self.connect_wireless_ip)
        connect_layout.addWidget(btn_connect_ip)

        layout.addWidget(connect_box)

        search_layout = QHBoxLayout()
        self.device_search = QLineEdit()
        self.device_search.setPlaceholderText("Search by model or serial")
        self.device_search.textChanged.connect(self.render_device_cards)
        search_layout.addWidget(self.device_search)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.devices_container = QWidget()
        self.devices_layout = QVBoxLayout(self.devices_container)
        self.devices_layout.setContentsMargins(0, 0, 0, 0)
        self.devices_layout.setSpacing(12)
        self.devices_layout.addStretch()

        scroll_area.setWidget(self.devices_container)
        layout.addWidget(scroll_area, 1)

        self.content_pages.addWidget(tab)

    # -------------------------------------------------------------------------
    # TAB 2: GLOBAL & AUDIO SETTINGS
    # -------------------------------------------------------------------------
    def build_global_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        group_engine = QGroupBox("Mirror Engine & Video Encoding")
        eng_layout = QGridLayout(group_engine)
        eng_layout.setSpacing(16)

        eng_layout.addWidget(QLabel("Primary Mirror Engine:"), 0, 0)
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["scrcpy 4.0 (Default)", "QtScrcpy (Gaming Engine)"])
        self.combo_engine.setToolTip(
            "• What it does: Selects the underlying mirror stream engine.\n"
            "• BEST CHOICE: 'scrcpy 4.0 (Default)' — Highest stability, sharpest video quality, and lowest latency.\n"
            "• ALTERNATIVE: 'QtScrcpy (Gaming Engine)' — Choose if playing fast competitive mobile games requiring keyboard keymapping."
        )
        eng_layout.addWidget(self.combo_engine, 0, 1)

        eng_layout.addWidget(QLabel("Video Bitrate:"), 0, 2)
        self.combo_bitrate = QComboBox()
        self.combo_bitrate.addItems(["16M", "8M", "4M", "2M"])
        self.combo_bitrate.setCurrentText("8M")
        self.combo_bitrate.setToolTip(
            "• What it does: Controls video stream data rate and visual sharpness.\n"
            "• BEST CHOICE: '8M' — Optimal balance between high-definition clarity and smooth streaming.\n"
            "• '16M': Maximum quality for gaming.\n"
            "• '4M' / '2M': Saves bandwidth on slow Wi-Fi networks."
        )
        eng_layout.addWidget(self.combo_bitrate, 0, 3)

        eng_layout.addWidget(QLabel("Video Codec:"), 1, 0)
        self.combo_codec = QComboBox()
        self.combo_codec.addItems(["h265", "h264", "av1"])
        self.combo_codec.setToolTip(
            "• What it does: Compression algorithm used to stream video.\n"
            "• BEST CHOICE: 'h265' — Higher visual quality with 50% lower Wi-Fi bandwidth usage.\n"
            "• 'h264': Universal hardware compatibility on older GPUs."
        )
        eng_layout.addWidget(self.combo_codec, 1, 1)

        eng_layout.addWidget(QLabel("Audio Source:"), 1, 2)
        self.combo_audio_source = QComboBox()
        self.combo_audio_source.addItems(["output", "mic"])
        self.combo_audio_source.setToolTip(
            "• What it does: Chooses audio capture source from Android device.\n"
            "• BEST CHOICE: 'output' — Streams game, music, and app audio directly to PC speakers.\n"
            "• 'mic': Routes phone microphone input to PC."
        )
        eng_layout.addWidget(self.combo_audio_source, 1, 3)

        layout.addWidget(group_engine)

        group_switches = QGroupBox("Privacy & Session Controls")
        sw_layout = QVBoxLayout(group_switches)

        self.chk_audio = QCheckBox("Enable Audio Forwarding (Android 11+ required)")
        self.chk_audio.setChecked(True)
        self.chk_audio.setToolTip(
            "• What it does: Forwards phone audio to PC speakers in real-time (Android 11+ required).\n"
            "• BEST CHOICE: Enabled (Checked)."
        )
        sw_layout.addWidget(self.chk_audio)

        self.chk_mute_pc = QCheckBox("Mute PC Playback (Keep recording sound enabled)")
        self.chk_mute_pc.setToolTip(
            "• What it does: Mutes audio from PC speakers while still capturing audio inside recorded video files.\n"
            "• BEST CHOICE: Disabled for normal listening; Enabled for quiet/stealth recording."
        )
        sw_layout.addWidget(self.chk_mute_pc)

        self.chk_stay_awake = QCheckBox("Stay Awake (Prevent device sleep while connected)")
        self.chk_stay_awake.setToolTip(
            "• What it does: Prevents your phone screen from timing out or sleeping while connected to PC.\n"
            "• BEST CHOICE: Enabled (Checked) — Keeps connection active."
        )
        sw_layout.addWidget(self.chk_stay_awake)

        self.chk_always_on_top = QCheckBox("Mirror Window Always-On-Top")
        self.chk_always_on_top.setToolTip(
            "• What it does: Keeps phone mirror window pinned on top of all other PC windows.\n"
            "• BEST CHOICE: Optional (Enable if multitasking while monitoring phone)."
        )
        sw_layout.addWidget(self.chk_always_on_top)

        self.chk_fullscreen = QCheckBox("Launch Mirror in Fullscreen")
        self.chk_fullscreen.setToolTip(
            "• What it does: Launches mirror window expanded to full PC screen.\n"
            "• BEST CHOICE: Optional (Best for gaming or presentations)."
        )
        sw_layout.addWidget(self.chk_fullscreen)

        layout.addWidget(group_switches)

        extra_layout = QHBoxLayout()
        extra_layout.addWidget(QLabel("Extra scrcpy flags:"))
        self.txt_extra_args = QLineEdit()
        self.txt_extra_args.setPlaceholderText("e.g. --shortcut-mod=lalt --max-size=1920")
        self.txt_extra_args.setToolTip(
            "• What it does: Pass custom advanced flags directly to scrcpy engine.\n"
            "• EXAMPLES: '--turn-screen-off' (Turns physical phone screen off while keeping PC mirror bright to save battery), '--max-fps=60'."
        )
        extra_layout.addWidget(self.txt_extra_args)
        layout.addLayout(extra_layout)

        layout.addStretch()

        self.content_pages.addWidget(tab)

    # -------------------------------------------------------------------------
    # TAB 4: PRESETS & HISTORY
    # -------------------------------------------------------------------------
    def build_presets_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        group_presets = QGroupBox("Presets Manager")
        pr_layout = QHBoxLayout(group_presets)

        pr_layout.addWidget(QLabel("Preset:"))
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(list(self.presets.keys()))
        pr_layout.addWidget(self.combo_presets, 1)

        btn_apply_preset = QPushButton("Apply")
        btn_apply_preset.clicked.connect(self.apply_selected_preset)
        pr_layout.addWidget(btn_apply_preset)

        btn_save_preset = QPushButton("Save Current")
        btn_save_preset.clicked.connect(self.save_current_as_preset)
        pr_layout.addWidget(btn_save_preset)

        btn_export = QPushButton("Export")
        btn_export.clicked.connect(self.export_presets)
        pr_layout.addWidget(btn_export)

        btn_import = QPushButton("Import")
        btn_import.clicked.connect(self.import_presets)
        pr_layout.addWidget(btn_import)

        layout.addWidget(group_presets)

        group_history = QGroupBox("Recent Session History")
        hist_layout = QVBoxLayout(group_history)

        history_search = QLineEdit()
        history_search.setPlaceholderText("Search session history")
        history_search.textChanged.connect(self.filter_history_table)
        hist_layout.addWidget(history_search)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["Timestamp", "Device Serial", "Bitrate", "Resolution", "Framerate"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.setSortingEnabled(True)
        hist_layout.addWidget(self.table_history)

        layout.addWidget(group_history, 1)
        self.update_history_table()

        self.content_pages.addWidget(tab)

    # -------------------------------------------------------------------------
    # TAB 5: IOS AIRPLAY
    # -------------------------------------------------------------------------
    def build_ios_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        group_ios = QGroupBox("AirPlay Receiver Engine (UxPlay)")
        ios_layout = QVBoxLayout(group_ios)
        ios_layout.setSpacing(14)

        info_lbl = QLabel(
            "Receive screen mirroring from iPhones, iPads, and Macs over local Wi-Fi.\n"
            "UxPlay hosts an AirPlay service visible as 'Morppy AirPlay Receiver'."
        )
        info_lbl.setStyleSheet("color: #94a3b8;")
        ios_layout.addWidget(info_lbl)

        btn_layout = QHBoxLayout()
        self.btn_ios_toggle = QPushButton("Launch AirPlay Mirror Receiver")
        self.btn_ios_toggle.setObjectName("purpleBtn")
        self.btn_ios_toggle.clicked.connect(self.toggle_airplay_server)
        btn_layout.addWidget(self.btn_ios_toggle)

        btn_focus_ios = QPushButton("🗔 Bring AirPlay to Front")
        btn_focus_ios.clicked.connect(self.focus_airplay_window)
        btn_layout.addWidget(btn_focus_ios)

        ios_layout.addLayout(btn_layout)

        self.ios_status_lbl = QLabel("AirPlay Status: Stopped")
        self.ios_status_lbl.setStyleSheet("color: #f43f5e; font-weight: bold;")
        ios_layout.addWidget(self.ios_status_lbl)

        layout.addWidget(group_ios)
        layout.addStretch()

        self.content_pages.addWidget(tab)

    # -------------------------------------------------------------------------
    # TAB 6: LOGS CONSOLE
    # -------------------------------------------------------------------------
    def build_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console, 1)

        btn_clear_logs = QPushButton("Clear Console Logs")
        btn_clear_logs.clicked.connect(self.log_console.clear)
        layout.addWidget(btn_clear_logs)

        self.content_pages.addWidget(tab)

    # -------------------------------------------------------------------------
    # SYSTEM TRAY SETUP
    # -------------------------------------------------------------------------
    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(Qt.SP_ComputerIcon if hasattr(Qt, 'SP_ComputerIcon') else 0))

        tray_menu = QMenu()
        act_show = QAction("Show Morppy", self)
        act_show.triggered.connect(self.showNormal)
        tray_menu.addAction(act_show)

        act_refresh = QAction("Refresh Devices", self)
        act_refresh.triggered.connect(self.start_device_scan)
        tray_menu.addAction(act_refresh)

        tray_menu.addSeparator()
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        tray_menu.addAction(act_exit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # -------------------------------------------------------------------------
    # DEVICE CARD RENDERING & GEAR ICON DISPLAY SETTINGS DIALOG
    # -------------------------------------------------------------------------
    def open_display_settings_dialog(self, serial=None):
        dialog = DisplaySettingsDialog(self, serial=serial, is_launch=False)
        dialog.exec_()

    def open_recording_settings_dialog(self, serial=None):
        dialog = RecordingSettingsDialog(self, serial=serial)
        dialog.exec_()

    def render_device_cards(self):
        while self.devices_layout.count() > 1:
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.known_devices:
            lbl_empty = QLabel("No Android devices found\nConnect a device by USB or enter a wireless address above.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            self.devices_layout.insertWidget(0, lbl_empty)
            return

        query = self.device_search.text().strip().lower() if hasattr(self, "device_search") else ""
        visible_devices = []
        for serial in self.known_devices:
            info = AndroidManager.get_device_info(serial)
            if query and query not in f"{serial} {info.get('model', '')}".lower():
                continue
            visible_devices.append((serial, info))

        if not visible_devices:
            lbl_empty = QLabel("No devices match your search.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            self.devices_layout.insertWidget(0, lbl_empty)
            return

        for serial, info in visible_devices:
            card = QFrame()
            card.setObjectName("cardFrame")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(12)

            # Top row: Serial & Model + Battery
            top_row = QHBoxLayout()
            lbl_title = QLabel(info["model"])
            lbl_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
            lbl_title.setStyleSheet("color: #38bdf8;")

            lbl_serial = QLabel(serial)
            lbl_serial.setStyleSheet("color: #94a3b8;")

            lbl_connection = QLabel("USB" if ":" not in serial else "Wireless")
            lbl_connection.setStyleSheet("color: #34d399; border: 1px solid rgba(16,185,129,.35); border-radius: 10px; padding: 4px 8px;")

            lbl_battery = QLabel(info["battery"])
            lbl_battery.setStyleSheet("color: #34d399; font-weight: bold;")

            top_row.addWidget(lbl_title)
            top_row.addWidget(lbl_serial)
            top_row.addStretch()
            top_row.addWidget(lbl_connection)
            top_row.addWidget(lbl_battery)
            card_layout.addLayout(top_row)

            # Live Telemetry Stats Row
            telemetry_row = QHBoxLayout()
            lbl_cpu = QLabel("CPU: --")
            lbl_cpu.setObjectName(f"cpu_{serial}")
            lbl_ram = QLabel("RAM: --")
            lbl_ram.setObjectName(f"ram_{serial}")

            telemetry_row.addWidget(lbl_cpu)
            telemetry_row.addWidget(lbl_ram)
            telemetry_row.addStretch()
            card_layout.addLayout(telemetry_row)

            # Primary Session Actions Row
            btn_row = QHBoxLayout()

            btn_mirror = QPushButton("Launch Mirror")
            btn_mirror.setObjectName("successBtn")
            btn_mirror.clicked.connect(lambda _, s=serial: self.launch_mirror_session(s))

            btn_reset_res = QPushButton("Reset Screen")
            btn_reset_res.setToolTip("Resets phone screen resolution & density to default native mode.")
            btn_reset_res.clicked.connect(lambda _, s=serial: (AndroidManager.reset_hardware_resolution(s), self.log_message(f"Reset resolution for {s}.")))

            btn_screen_off = QPushButton("Screen Off")
            btn_screen_off.setToolTip("Turns OFF physical phone display while keeping PC mirror stream 100% active to save battery & protect screen.")
            btn_screen_off.clicked.connect(lambda _, s=serial: (AndroidManager.turn_off_screen(s), self.log_message(f"Turned OFF physical display for {s}.")))

            btn_lock = QPushButton("Lock")
            btn_lock.clicked.connect(lambda _, s=serial: AndroidManager.lock_device(s))

            btn_reboot = QPushButton("Reboot")
            btn_reboot.setObjectName("dangerBtn")
            btn_reboot.clicked.connect(lambda _, s=serial: self.confirm_reboot(s))

            is_rec = self.recording_sessions.get(serial, False)
            btn_rec = QPushButton("Recording" if is_rec else "Start Recording")
            btn_rec.setObjectName(f"rec_btn_{serial}")
            if is_rec:
                btn_rec.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(249, 115, 22, 0.35);
                        color: #ffedd5;
                        border: 1px solid #f97316;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(249, 115, 22, 0.5);
                        border-color: #fb923c;
                    }
                """)
            else:
                btn_rec.setToolTip("Start screen recording on this device.")

            btn_rec.clicked.connect(lambda _, s=serial: self.toggle_recording_session(s))

            btn_row.addWidget(btn_mirror)
            btn_row.addWidget(btn_reset_res)
            btn_row.addWidget(btn_screen_off)
            btn_row.addWidget(btn_lock)
            btn_row.addWidget(btn_reboot)
            btn_row.addWidget(btn_rec)

            card_layout.addLayout(btn_row)

            # Screen Control Quick Toolbar
            toolbar_box = QFrame()
            toolbar_box.setObjectName("toolbarFrame")
            tb_layout = QHBoxLayout(toolbar_box)
            tb_layout.setContentsMargins(6, 4, 6, 4)
            tb_layout.setSpacing(6)

            btn_pow = QPushButton("Power")
            btn_pow.setObjectName("toolBtn")
            btn_pow.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 26))

            btn_volp = QPushButton("Vol+")
            btn_volp.setObjectName("toolBtn")
            btn_volp.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 24))

            btn_volm = QPushButton("Vol-")
            btn_volm.setObjectName("toolBtn")
            btn_volm.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 25))

            btn_back = QPushButton("Back")
            btn_back.setObjectName("toolBtn")
            btn_back.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 4))

            btn_home = QPushButton("Home")
            btn_home.setObjectName("toolBtn")
            btn_home.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 3))

            btn_recents = QPushButton("Recents")
            btn_recents.setObjectName("toolBtn")
            btn_recents.clicked.connect(lambda _, s=serial: AndroidManager.send_keyevent(s, 187))

            btn_clip = QPushButton("Clipboard")
            btn_clip.setObjectName("toolBtn")
            btn_clip.clicked.connect(lambda _, s=serial: self.prompt_inject_text(s))

            btn_snap = QPushButton("Screenshot")
            btn_snap.setObjectName("toolBtn")
            btn_snap.clicked.connect(lambda _, s=serial: AndroidManager.take_screenshot(
                s, self.recording_settings.get("path", SCRCPY_DIRECTORY)
            ))

            tb_layout.addWidget(btn_pow)
            tb_layout.addWidget(btn_volp)
            tb_layout.addWidget(btn_volm)
            tb_layout.addWidget(btn_back)
            tb_layout.addWidget(btn_home)
            tb_layout.addWidget(btn_recents)
            tb_layout.addWidget(btn_clip)
            tb_layout.addWidget(btn_snap)

            card_layout.addWidget(toolbar_box)

            self.devices_layout.insertWidget(self.devices_layout.count() - 1, card)

    def prompt_inject_text(self, serial):
        text, ok = QInputDialog.getText(self, "Inject Text / Clipboard", "Enter text to send to mobile phone:")
        if ok and text:
            AndroidManager.inject_text(serial, text)
            self.log_message(f"Injected text to {serial}.")

    # -------------------------------------------------------------------------
    # TELEMETRY & ACTIONS
    # -------------------------------------------------------------------------
    def start_device_scan(self):
        self.status_badge.setText("Scanning Devices")
        self.status_badge.setStyleSheet("""
            background-color: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            font-weight: bold;
            padding: 6px 14px;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 14px;
        """)
        self.scanner_thread = DeviceScannerWorker()
        self.scanner_thread.devices_signal.connect(self.on_devices_scanned)
        self.scanner_thread.start()

    def on_devices_scanned(self, devices):
        self.known_devices = devices
        count = len(devices)
        self.status_badge.setText(f"{count} Device{'s' if count != 1 else ''} Connected")
        self.status_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #34d399;
            font-weight: bold;
            padding: 6px 14px;
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 14px;
        """)
        self.render_device_cards()

    def update_telemetry(self):
        devices = self.known_devices or list(self.active_sessions.keys())
        if not devices:
            return
        self.telemetry_worker = TelemetryWorker(devices)
        self.telemetry_worker.telemetry_signal.connect(self.on_telemetry_updated)
        self.telemetry_worker.start()

    def on_telemetry_updated(self, serial, telemetry):
        cpu_lbl = self.findChild(QLabel, f"cpu_{serial}")
        ram_lbl = self.findChild(QLabel, f"ram_{serial}")

        if cpu_lbl: cpu_lbl.setText(f"CPU: {telemetry.get('cpu', '--')}")
        if ram_lbl: ram_lbl.setText(f"RAM: {telemetry.get('ram', '--')}")

    def animate_recording_blink(self):
        self.rec_blink_state = not self.rec_blink_state
        for serial, is_rec in list(self.recording_sessions.items()):
            if is_rec:
                btn = self.findChild(QPushButton, f"rec_btn_{serial}")
                if btn:
                    try:
                        btn.setText("Recording" if self.rec_blink_state else "Recording...")
                    except RuntimeError:
                        pass

    def toggle_recording_session(self, serial, btn=None):
        live_btn = self.findChild(QPushButton, f"rec_btn_{serial}") or btn
        is_currently_recording = self.recording_sessions.get(serial, False)
        if not is_currently_recording:
            dialog = RecordingSettingsDialog(self, serial=serial)
            if dialog.exec_() != QDialog.Accepted:
                self.log_message(f"Screen recording launch cancelled for {serial}.")
                return

            eng = self.recording_settings.get("engine", "ADB Native MediaCodec (On-Device Phone GPU)")
            fmt = self.recording_settings.get("format", "mp4")
            save_path = self.recording_settings.get("path", SCRCPY_DIRECTORY)
            res = AndroidManager.start_screenrecord(serial, format_ext=fmt, engine_type=eng, save_folder=save_path)
            if res:
                self.recording_sessions[serial] = True
                if live_btn:
                    try:
                        live_btn.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(249, 115, 22, 0.35);
                                color: #ffedd5;
                                border: 1px solid #f97316;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: rgba(249, 115, 22, 0.5);
                                border-color: #fb923c;
                            }
                        """)
                        live_btn.setText("Recording")
                    except RuntimeError:
                        pass
                self.log_message(f"Started screen recording on {serial} ({fmt.upper()}). Target path: {res}")
            else:
                QMessageBox.critical(self, "Recording Failed", f"Could not start screen recording on {serial}.")
        else:
            reply = QMessageBox.question(
                self,
                "Stop Recording",
                f"Stop screen recording on {serial}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply != QMessageBox.Yes:
                return
            self.recording_sessions[serial] = False
            if live_btn:
                try:
                    live_btn.setStyleSheet("""
                        QPushButton {
                            background-color: rgba(239, 68, 68, 0.2);
                            color: #fca5a5;
                            border: 1px solid #ef4444;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: rgba(239, 68, 68, 0.35);
                            border-color: #f87171;
                        }
                    """)
                    live_btn.setText("Start Recording")
                except RuntimeError:
                    pass
            save_dir = self.recording_settings.get("path", SCRCPY_DIRECTORY)
            saved_path = AndroidManager.stop_screenrecord(serial, local_folder=save_dir)
            if isinstance(saved_path, str) and os.path.exists(saved_path):
                self.log_message(f"Screen recording saved successfully to: {saved_path}")
                try:
                    os.startfile(os.path.dirname(saved_path))
                except Exception:
                    pass
            else:
                self.log_message(f"Stopped recording on {serial}. Saved to folder: {save_dir}")

    def connect_wireless_ip(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Invalid Input", "Please enter an IP address (e.g. 192.168.1.35:5555)")
            return
        self.log_message(f"Connecting to wireless device {ip}...")
        ok, res = AndroidManager.connect_ip(ip)
        if ok:
            self.log_message(f"Connected to {ip}: {res}")
            self.start_device_scan()
        else:
            QMessageBox.critical(self, "Connection Failed", f"Could not connect to {ip}:\n{res}")

    def reset_adb_server(self):
        reply = QMessageBox.question(
            self,
            "Reset ADB Server",
            "Reset the Android Debug Bridge server and reconnect devices?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        self.log_message("Resetting ADB server...")
        if AndroidManager.reset_adb():
            self.log_message("ADB server restarted successfully.")
            self.start_device_scan()

    def confirm_reboot(self, serial):
        reply = QMessageBox.question(
            self,
            "Reboot Device",
            f"Reboot the device {serial}? Unsaved work may be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            AndroidManager.reboot_device(serial)

    def launch_mirror_session(self, serial):
        dialog = DisplaySettingsDialog(self, serial=serial, is_launch=True)
        if dialog.exec_() != QDialog.Accepted:
            self.log_message(f"Mirror session launch cancelled for {serial}.")
            return

        settings = self.get_current_settings()
        self.log_message(f"Launching mirror session for {serial} using {settings.get('mirror_engine')}...")

        proc = AndroidManager.launch_scrcpy(serial, settings)
        self.active_sessions[serial] = {
            "process": proc,
            "pid": proc.pid,
            "hw_res": settings.get("hardware_res"),
            "card_data": {}
        }
        self.append_session_history(serial, settings)
        self.log_message(f"Mirror session started (PID {proc.pid}).")

    def toggle_airplay_server(self):
        if self.ios_manager.process and self.ios_manager.process.poll() is None:
            self.ios_manager.stop_server()
            self.btn_ios_toggle.setText("Launch AirPlay Mirror Receiver")
            self.ios_status_lbl.setText("AirPlay Status: Stopped")
            self.ios_status_lbl.setStyleSheet("color: #f43f5e; font-weight: bold;")
        else:
            if self.ios_manager.start_server():
                self.btn_ios_toggle.setText("Stop AirPlay Receiver")
                self.ios_status_lbl.setText("AirPlay Status: Running ('Morppy AirPlay Receiver')")
                self.ios_status_lbl.setStyleSheet("color: #34d399; font-weight: bold;")

    def focus_airplay_window(self):
        if not self.ios_manager.bring_to_front():
            QMessageBox.information(self, "AirPlay Window", "No active AirPlay video stream window found.")

    def get_current_settings(self):
        res_text = self.display_settings.get("resolution", "Default (Native)")
        hw_res = "Native (Safe)"
        if "1440p" in res_text:
            hw_res = "1440p (2K)"
        elif "2160p" in res_text:
            hw_res = "2160p (4K)"

        return {
            "mirror_engine": self.display_settings.get("engine", "scrcpy 4.0 (Default)"),
            "bitrate": self.combo_bitrate.currentText() if hasattr(self, 'combo_bitrate') else "8M",
            "codec": self.combo_codec.currentText() if hasattr(self, 'combo_codec') else "h265",
            "render": self.display_settings.get("render", "default"),
            "screen_off": self.display_settings.get("screen_off", True),
            "audio": self.chk_audio.isChecked() if hasattr(self, 'chk_audio') else True,
            "mute_pc": self.chk_mute_pc.isChecked() if hasattr(self, 'chk_mute_pc') else False,
            "record": self.chk_record_on_start.isChecked() if hasattr(self, 'chk_record_on_start') else False,
            "record_path": self.txt_rec_path.text() if hasattr(self, 'txt_rec_path') else SCRCPY_DIRECTORY,
            "record_format": self.combo_rec_format.currentText() if hasattr(self, 'combo_rec_format') else "mp4",
            "resolution": res_text,
            "hardware_res": hw_res,
            "window_size": self.display_settings.get("window_size", "Default"),
            "virtual_display": self.display_settings.get("virtual_display", False),
            "crop": self.display_settings.get("crop", ""),
            "audio_source": self.combo_audio_source.currentText() if hasattr(self, 'combo_audio_source') else "output",
            "stay_awake": self.chk_stay_awake.isChecked() if hasattr(self, 'chk_stay_awake') else False,
            "always_on_top": self.chk_always_on_top.isChecked() if hasattr(self, 'chk_always_on_top') else False,
            "fullscreen": self.chk_fullscreen.isChecked() if hasattr(self, 'chk_fullscreen') else False,
            "extra_args": self.txt_extra_args.text().strip() if hasattr(self, 'txt_extra_args') else "",
        }

    def load_presets(self):
        default_presets = {
            "Balanced": {"bitrate": "8M", "codec": "h265", "resolution": "Default (Native)", "audio": True},
            "Gaming": {"bitrate": "16M", "codec": "h265", "resolution": "1080p (Downscale)", "audio": False, "screen_off": True},
            "Recording": {"bitrate": "16M", "codec": "h265", "resolution": "1080p (Downscale)", "audio": True, "record": True},
            "Low Bandwidth": {"bitrate": "2M", "codec": "h264", "resolution": "720p (Downscale)", "audio": True},
        }
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict): return data
            except Exception: pass
        return default_presets

    def save_presets(self):
        try:
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2)
        except Exception: pass

    def apply_selected_preset(self):
        preset_name = self.combo_presets.currentText()
        if preset_name in self.presets:
            p = self.presets[preset_name]
            if "bitrate" in p: self.combo_bitrate.setCurrentText(p["bitrate"])
            if "codec" in p: self.combo_codec.setCurrentText(p["codec"])
            if "resolution" in p:
                self.display_settings["resolution"] = p["resolution"]
            if "audio" in p: self.chk_audio.setChecked(p["audio"])
            if "record" in p: self.recording_settings["auto_record"] = p["record"]
            if "screen_off" in p: self.display_settings["screen_off"] = p["screen_off"]
            self.log_message(f"Applied preset: {preset_name}")

    def apply_quick_preset(self, preset_name):
        if preset_name not in self.presets:
            return
        preset = self.presets[preset_name]
        if hasattr(self, "combo_bitrate") and "bitrate" in preset:
            self.combo_bitrate.setCurrentText(preset["bitrate"])
        if hasattr(self, "combo_codec") and "codec" in preset:
            self.combo_codec.setCurrentText(preset["codec"])
        if "resolution" in preset:
            self.display_settings["resolution"] = preset["resolution"]
        if hasattr(self, "chk_audio") and "audio" in preset:
            self.chk_audio.setChecked(preset["audio"])

    def save_current_as_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if ok and name.strip():
            self.presets[name.strip()] = self.get_current_settings()
            self.save_presets()
            self.combo_presets.clear()
            self.combo_presets.addItems(list(self.presets.keys()))
            self.combo_presets.setCurrentText(name.strip())
            self.log_message(f"Saved new preset: {name.strip()}")

    def export_presets(self):
        target, _ = QFileDialog.getSaveFileName(self, "Export Presets", "scrcpy_presets_export.json", "JSON Files (*.json)")
        if target:
            try:
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(self.presets, f, indent=2)
                self.log_message("Presets exported successfully.")
            except Exception as e:
                self.log_message(f"Export error: {e}")

    def import_presets(self):
        target, _ = QFileDialog.getOpenFileName(self, "Import Presets", "", "JSON Files (*.json)")
        if target:
            try:
                with open(target, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.presets = data
                    self.save_presets()
                    self.combo_presets.clear()
                    self.combo_presets.addItems(list(self.presets.keys()))
                    self.log_message("Presets imported successfully.")
            except Exception as e:
                self.log_message(f"Import error: {e}")

    def load_session_history(self):
        if os.path.exists(SESSION_HISTORY_FILE):
            try:
                with open(SESSION_HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception: pass
        return []

    def save_session_history(self):
        try:
            with open(SESSION_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.session_history, f, indent=2)
        except Exception: pass

    def append_session_history(self, serial, settings):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "serial": serial,
            "bitrate": settings.get("bitrate", "8M"),
            "resolution": settings.get("resolution", "Default"),
        }
        self.session_history = [entry] + self.session_history[:19]
        self.save_session_history()
        self.update_history_table()

    def update_history_table(self):
        self.table_history.setRowCount(len(self.session_history))
        for row, entry in enumerate(self.session_history):
            self.table_history.setItem(row, 0, QTableWidgetItem(entry.get("timestamp", "")))
            self.table_history.setItem(row, 1, QTableWidgetItem(entry.get("serial", "")))
            self.table_history.setItem(row, 2, QTableWidgetItem(entry.get("bitrate", "")))
            self.table_history.setItem(row, 3, QTableWidgetItem(entry.get("resolution", "")))
            self.table_history.setItem(row, 4, QTableWidgetItem(entry.get("framerate", "60 fps")))

    def filter_history_table(self, text):
        text = text.strip().lower()
        for row in range(self.table_history.rowCount()):
            match = any(
                text in (self.table_history.item(row, column).text().lower()
                         if self.table_history.item(row, column) else "")
                for column in range(self.table_history.columnCount())
            )
            self.table_history.setRowHidden(row, bool(text) and not match)

    def browse_record_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Recording Directory")
        if folder:
            self.txt_rec_path.setText(folder)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.log_console.append(formatted)

    def closeEvent(self, event):
        for serial, session in list(self.active_sessions.items()):
            proc = session.get("process")
            if proc:
                try: proc.kill()
                except Exception: pass
            AndroidManager.reset_hardware_resolution(serial)
        self.ios_manager.stop_server()
        event.accept()


# -----------------------------------------------------------------------------
# MAIN ENTRYPOINT WITH BOOT SPLASH ANIMATION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Splash Screen Boot Animation
    splash = MorppySplashScreen()
    splash.show()

    steps = [
        (25, "Initializing Morppy Core Engines..."),
        (55, "Verifying ADB & Scrcpy Drivers..."),
        (85, "Loading UxPlay AirPlay Receiver Services..."),
        (100, "Ready to launch Morppy")
    ]

    for val, msg in steps:
        splash.set_progress(val, msg)
        time.sleep(0.25)

    window = MorppyMainWindow()
    splash.finish(window)
    window.show()

    sys.exit(app.exec_())
