import json
import os
from cute_puppy.platform import get_platform

platform_handler = get_platform()
APP_DATA_DIR = platform_handler.get_appdata_dir()
CONFIG_PATH = os.path.join(APP_DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "puppy_name": "Milo",
    "speed": "Normal",
    "puppy_size": "Small",
    "coat_style": "Brown & Cream",
    "collar_color": "Blue",
    "active_toy": "Ball",
    "follow_cursor": True,
    "random_wandering": True,
    "auto_sleep": True,
    "random_speech": True,
    "smart_idle_sleep": True,
    "sound_enabled": True,
    "sound_volume": 60,
    "start_with_windows": True,
    "performance_mode": False,
    "hunger": 20.0,
    "thirst": 20.0,
    "energy": 95.0,
    "happiness": 85.0,
    "affection": 65.0,
    "home_x": None,
    "home_y": None,
    "home_theme": "Cozy Wood",
    "unlocked_achievements": []
}

SPEED_MULTIPLIERS = {
    "Slow": 0.65,
    "Normal": 1.0,
    "Fast": 1.5
}

SIZE_SCALES = {
    "Tiny": 0.5,
    "Small": 0.75,
    "Normal": 1.0,
    "Large": 1.35,
    "Giant": 1.75
}

class SettingsManager:
    def __init__(self, filepath=CONFIG_PATH):
        self.filepath = filepath
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = DEFAULT_SETTINGS.copy()
        else:
            self.save()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
        if key in ("start_with_windows", "start_with_macos"):
            self.toggle_autostart(value)

    def toggle_autostart(self, enable: bool):
        platform_handler.register_autostart("", enable)

    @property
    def speed_factor(self):
        return SPEED_MULTIPLIERS.get(self.settings.get("speed", "Normal"), 1.0)

    @property
    def size_scale(self):
        return SIZE_SCALES.get(self.settings.get("puppy_size", "Small"), 0.75)
