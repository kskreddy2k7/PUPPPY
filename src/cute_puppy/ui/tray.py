import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Signal, QObject
from cute_puppy.platform.common import get_asset_path

class TrayIconManager(QObject):
    def __init__(self, puppy_window, settings_manager, parent=None):
        super().__init__(parent)
        self.puppy = puppy_window
        self.settings = settings_manager

        name = self.settings.get("puppy_name", "Milo")
        self.tray = QSystemTrayIcon(self)

        asset_path = get_asset_path("puppy", "brown_cream", "idle", "frame_0.png")
        pixmap = QPixmap(asset_path)
        if pixmap.isNull():
            pixmap = QPixmap(32, 32)
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip(f"Cute Desktop Puppy ({name})")

        self.menu = QMenu()
        self.build_menu()
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def build_menu(self):
        self.menu.clear()

        name = self.settings.get("puppy_name", "Milo")
        mood_val = self.puppy.personality.current_mood.value

        title_act = self.menu.addAction(f"🐶 {name}")
        title_act.setEnabled(False)

        mood_act = self.menu.addAction(f"❤️ Mood: {mood_val}")
        mood_act.setEnabled(False)

        self.menu.addSeparator()

        show_act = self.menu.addAction("👀 Show Puppy")
        show_act.triggered.connect(self.puppy.show)

        hide_act = self.menu.addAction("🙈 Hide Puppy")
        hide_act.triggered.connect(self.puppy.hide)

        follow_act = self.menu.addAction("🖱 Follow Cursor")
        follow_act.setCheckable(True)
        follow_act.setChecked(self.settings.get("follow_cursor", True))
        follow_act.triggered.connect(lambda c: self.settings.set("follow_cursor", c))

        wander_act = self.menu.addAction("🐾 Autonomous Mode")
        wander_act.setCheckable(True)
        wander_act.setChecked(self.settings.get("random_wandering", True))
        wander_act.triggered.connect(lambda c: self.settings.set("random_wandering", c))

        self.menu.addSeparator()

        play_act = self.menu.addAction("🎉 Play")
        play_act.triggered.connect(self.puppy.trigger_random_expression)

        ball_act = self.menu.addAction("🎾 Throw Ball")
        ball_act.triggered.connect(self.puppy.play_with_toy_routine)

        feed_act = self.menu.addAction("🍖 Feed")
        feed_act.triggered.connect(self.puppy.start_eating_routine)

        water_act = self.menu.addAction("💧 Water")
        water_act.triggered.connect(self.puppy.start_drinking_routine)

        self.menu.addSeparator()

        home_act = self.menu.addAction("🏠 Go Home")
        home_act.triggered.connect(self.puppy.start_sleep_routine)

        sleep_act = self.menu.addAction("😴 Sleep")
        sleep_act.triggered.connect(self.puppy.start_sleep_routine)

        wake_act = self.menu.addAction("🌅 Wake Up")
        wake_act.triggered.connect(self.puppy.wake_up_routine)

        self.menu.addSeparator()

        pause_text = "▶ Resume" if self.puppy.is_paused else "⏸ Pause"
        pause_act = self.menu.addAction(pause_text)
        pause_act.triggered.connect(self.puppy.toggle_pause)

        settings_act = self.menu.addAction("⚙ Settings")
        settings_act.triggered.connect(lambda: self.puppy.request_settings_signal.emit())

        self.menu.addSeparator()

        exit_act = self.menu.addAction("❌ Quit")
        exit_act.triggered.connect(QApplication.quit)
