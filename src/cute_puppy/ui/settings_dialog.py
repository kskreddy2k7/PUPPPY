import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QFormLayout, QTabWidget, QProgressBar, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from cute_puppy.behavior.achievements import ACHIEVEMENTS_LIST
from cute_puppy.platform.common import get_version

class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager

        self.setWindowTitle(f"Cute Puppy Settings & Profile (v{get_version()})")
        self.setFixedSize(420, 560)

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFDF9;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #EADBCE;
                background: #FFFFFF;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #F4ECE1;
                color: #5A3D28;
                padding: 6px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #D48C4B;
            }
            QGroupBox {
                font-weight: bold;
                color: #5A3D28;
                border: 2px solid #EADBCE;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QLabel {
                color: #4A3525;
            }
            QLineEdit, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D5C4B5;
                border-radius: 5px;
                padding: 5px;
                color: #4A3525;
            }
            QCheckBox {
                color: #4A3525;
            }
            QPushButton {
                background-color: #D48C4B;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #B87638;
            }
        """)

        layout = QVBoxLayout(self)
        tabs = QTabWidget(self)

        # Tab 1: Puppy Profile & Stats
        tab_puppy = QWidget()
        l_pup = QVBoxLayout(tab_puppy)

        grp_stats = QGroupBox("Puppy Affection & Metrics", tab_puppy)
        f_stats = QFormLayout(grp_stats)

        self.bar_aff = QProgressBar()
        self.bar_aff.setValue(self.settings.get("affection", 60))
        self.bar_aff.setStyleSheet("QProgressBar::chunk { background-color: #FF7096; }")
        f_stats.addRow("Affection:", self.bar_aff)

        self.bar_hap = QProgressBar()
        self.bar_hap.setValue(self.settings.get("happiness", 85))
        self.bar_hap.setStyleSheet("QProgressBar::chunk { background-color: #FFB347; }")
        f_stats.addRow("Happiness:", self.bar_hap)

        self.bar_ene = QProgressBar()
        self.bar_ene.setValue(self.settings.get("energy", 95))
        self.bar_ene.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        f_stats.addRow("Energy:", self.bar_ene)

        l_pup.addWidget(grp_stats)

        grp_bas = QGroupBox("Basics", tab_puppy)
        f_bas = QFormLayout(grp_bas)

        self.name_edit = QLineEdit(self.settings.get("puppy_name", "Milo"))
        f_bas.addRow("Puppy Name:", self.name_edit)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Slow", "Normal", "Fast"])
        self.speed_combo.setCurrentText(self.settings.get("speed", "Normal"))
        f_bas.addRow("Speed:", self.speed_combo)

        self.size_combo = QComboBox()
        self.size_combo.addItems(["Tiny", "Small", "Normal", "Large", "Giant"])
        self.size_combo.setCurrentText(self.settings.get("puppy_size", "Small"))
        f_bas.addRow("Size:", self.size_combo)

        l_pup.addWidget(grp_bas)
        tabs.addTab(tab_puppy, "🐶 Puppy")

        # Tab 2: Appearance & Customization
        tab_app = QWidget()
        l_app = QVBoxLayout(tab_app)

        grp_app = QGroupBox("Styles & Toys", tab_app)
        f_app = QFormLayout(grp_app)

        self.coat_combo = QComboBox()
        self.coat_combo.addItems(["Brown & Cream", "White", "Golden", "Black & White"])
        self.coat_combo.setCurrentText(self.settings.get("coat_style", "Brown & Cream"))
        f_app.addRow("Fur Coat Style:", self.coat_combo)

        self.collar_combo = QComboBox()
        self.collar_combo.addItems(["Blue", "Red", "Pink", "Green"])
        self.collar_combo.setCurrentText(self.settings.get("collar_color", "Blue"))
        f_app.addRow("Collar Color:", self.collar_combo)

        self.toy_combo = QComboBox()
        self.toy_combo.addItems(["Ball", "Blue Ball", "Bone", "Rope", "Teddy"])
        self.toy_combo.setCurrentText(self.settings.get("active_toy", "Ball"))
        f_app.addRow("Active Toy:", self.toy_combo)

        l_app.addWidget(grp_app)
        tabs.addTab(tab_app, "🎨 Appearance")

        # Tab 3: Behavior & Sound
        tab_beh = QWidget()
        l_beh = QVBoxLayout(tab_beh)

        grp_beh = QGroupBox("Behavior & Sleep", tab_beh)
        v_beh = QVBoxLayout(grp_beh)

        self.chk_follow = QCheckBox("Follow Mouse Cursor")
        self.chk_follow.setChecked(self.settings.get("follow_cursor", True))
        v_beh.addWidget(self.chk_follow)

        self.chk_wander = QCheckBox("Random Wandering")
        self.chk_wander.setChecked(self.settings.get("random_wandering", True))
        v_beh.addWidget(self.chk_wander)

        self.chk_smart = QCheckBox("Smart Idle Auto-Sleep (Inactivity)")
        self.chk_smart.setChecked(self.settings.get("smart_idle_sleep", True))
        v_beh.addWidget(self.chk_smart)

        self.chk_perf = QCheckBox("⚡ Performance Mode (Lower Idle CPU)")
        self.chk_perf.setChecked(self.settings.get("performance_mode", False))
        v_beh.addWidget(self.chk_perf)

        self.chk_autostart = QCheckBox("Start Cute Puppy at System Startup")
        self.chk_autostart.setChecked(self.settings.get("start_with_windows", True))
        v_beh.addWidget(self.chk_autostart)

        l_beh.addWidget(grp_beh)

        grp_snd = QGroupBox("Audio Sound", tab_beh)
        f_snd = QFormLayout(grp_snd)

        self.chk_sound = QCheckBox("Enable Sound Effects")
        self.chk_sound.setChecked(self.settings.get("sound_enabled", True))
        f_snd.addRow(self.chk_sound)

        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(self.settings.get("sound_volume", 60))
        f_snd.addRow("Volume:", self.vol_slider)

        l_beh.addWidget(grp_snd)
        tabs.addTab(tab_beh, "🎮 Behavior")

        # Tab 4: Achievements & About
        tab_ach = QWidget()
        l_ach = QVBoxLayout(tab_ach)

        lbl_version = QLabel(f"Cute Puppy Desktop App v{get_version()}", tab_ach)
        lbl_version.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_version.setAlignment(Qt.AlignCenter)
        l_ach.addWidget(lbl_version)

        unlocked = self.settings.get("unlocked_achievements", [])
        for key, (title, desc) in ACHIEVEMENTS_LIST.items():
            is_unlocked = key in unlocked
            lbl = QLabel(f"{'✅' if is_unlocked else '🔒'} {title}\n  {desc}", tab_ach)
            if not is_unlocked:
                lbl.setStyleSheet("color: #888888;")
            l_ach.addWidget(lbl)

        tabs.addTab(tab_ach, "🏆 Achievements")

        layout.addWidget(tabs)

        btn_box = QHBoxLayout()
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #B5A496;")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def save_settings(self):
        self.settings.set("puppy_name", self.name_edit.text().strip() or "Milo")
        self.settings.set("speed", self.speed_combo.currentText())
        self.settings.set("puppy_size", self.size_combo.currentText())

        self.settings.set("coat_style", self.coat_combo.currentText())
        self.settings.set("collar_color", self.collar_combo.currentText())
        self.settings.set("active_toy", self.toy_combo.currentText())

        self.settings.set("follow_cursor", self.chk_follow.isChecked())
        self.settings.set("random_wandering", self.chk_wander.isChecked())
        self.settings.set("smart_idle_sleep", self.chk_smart.isChecked())
        self.settings.set("performance_mode", self.chk_perf.isChecked())
        self.settings.set("start_with_windows", self.chk_autostart.isChecked())
        self.settings.set("start_with_macos", self.chk_autostart.isChecked())

        self.settings.set("sound_enabled", self.chk_sound.isChecked())
        self.settings.set("sound_volume", self.vol_slider.value())

        self.accept()
