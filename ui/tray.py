import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Signal, QObject

ASSET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "puppy", "brown_cream", "idle", "frame_0.png")

class TrayIconManager(QObject):
    def __init__(self, puppy_window, settings_manager, parent=None):
        super().__init__(parent)
        self.puppy = puppy_window
        self.settings = settings_manager

        name = self.settings.get("puppy_name", "Milo")
        self.tray = QSystemTrayIcon(self)

        pixmap = QPixmap(ASSET_PATH)
        if pixmap.isNull(): pixmap = QPixmap(32, 32)
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

        follow_act = self.menu.addAction("🖱 Follow Cursor")
        follow_act.setCheckable(True)
        follow_act.setChecked(self.settings.get("follow_cursor", True))
        follow_act.triggered.connect(lambda c: self.settings.set("follow_cursor", c))

        run_act = self.menu.addAction("🏃 Run")
        run_act.triggered.connect(lambda: self.settings.set("speed", "Fast"))

        sleep_act = self.menu.addAction("😴 Sleep")
        sleep_act.triggered.connect(self.puppy.start_sleep_routine)

        wake_act = self.menu.addAction("🌅 Wake Up")
        wake_act.triggered.connect(self.puppy.wake_up_routine)

        self.menu.addSeparator()

        rename_act = self.menu.addAction("✏ Rename Puppy")
        rename_act.triggered.connect(self.puppy.rename_puppy_dialog)

        pause_act = self.menu.addAction("⏸ Pause / Resume")
        pause_act.triggered.connect(self.puppy.toggle_pause)

        settings_act = self.menu.addAction("⚙ Settings")
        settings_act.triggered.connect(lambda: self.puppy.request_settings_signal.emit())

        self.menu.addSeparator()

        exit_act = self.menu.addAction("❌ Exit")
        exit_act.triggered.connect(QApplication.quit)
