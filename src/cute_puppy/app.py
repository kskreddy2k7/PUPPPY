import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSharedMemory
from PySide6.QtGui import QKeySequence, QShortcut

from cute_puppy.storage import SettingsManager
from cute_puppy.audio import SoundManager
from cute_puppy.animation import generate_all_assets
from cute_puppy.pet.house import HouseWindow
from cute_puppy.pet.toy import ToyWindow
from cute_puppy.pet.window import PuppyWindow
from cute_puppy.ui import TrayIconManager, SettingsDialog
from cute_puppy.platform.common import get_version

def main():
    if hasattr(sys.stdout, 'reconfigure') and sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8')
        
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 1. Single Instance Protection (Prevent Duplicate Puppies)
    shared_memory = QSharedMemory("CutePuppy_SingleInstance_Mutex")
    if not shared_memory.create(1):
        if shared_memory.error() == QSharedMemory.AlreadyExists:
            shared_memory.attach()
            shared_memory.detach()
            if not shared_memory.create(1):
                pass

    # 2. Startup Auto-Registration Verification
    settings = SettingsManager()
    if settings.get("start_with_windows", True) or settings.get("start_with_macos", True):
        try:
            settings.toggle_autostart(True)
        except Exception as e:
            print(f"Startup registration check: {e}")

    generate_all_assets()

    sound = SoundManager(settings)
    house = HouseWindow(settings)
    house.show()

    toy = ToyWindow(settings)

    puppy = PuppyWindow(settings, sound, house, toy)
    puppy.show()

    tray = TrayIconManager(puppy, settings)

    # Graceful Shutdown Event Handler
    def on_app_about_to_quit():
        try:
            settings.save()
            shared_memory.detach()
        except Exception:
            pass

    app.aboutToQuit.connect(on_app_about_to_quit)

    def open_settings():
        dialog = SettingsDialog(settings)
        if dialog.exec():
            tray.build_menu()
            house.update()
            scale = settings.size_scale
            w, h = int(72 * scale), int(72 * scale)
            puppy.setFixedSize(w, h)
            puppy.anim.load_all_sprites()

    puppy.request_settings_signal.connect(open_settings)

    # Shift+D Quick Shortcut for size toggle
    def handle_shift_d_shortcut():
        sizes = ["Tiny", "Small", "Normal", "Large", "Giant"]
        cur_size = settings.get("puppy_size", "Small")
        next_idx = (sizes.index(cur_size) + 1) % len(sizes) if cur_size in sizes else 0
        new_size = sizes[next_idx]
        puppy.change_puppy_size(new_size)
        puppy.trigger_random_expression()

    shortcut = QShortcut(QKeySequence("Shift+D"), puppy)
    shortcut.activated.connect(handle_shift_d_shortcut)

    print(f"Cute Desktop Puppy v{get_version()} running as native App!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
