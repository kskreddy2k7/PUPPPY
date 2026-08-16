import os
import sys
import winreg
from cute_puppy.platform.common import get_base_dir

class WindowsPlatform:
    REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "CutePuppy"

    def get_appdata_dir(self) -> str:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        target = os.path.join(appdata, "CutePuppy")
        os.makedirs(target, exist_ok=True)
        return target

    def register_autostart(self, app_path: str, enabled: bool):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY, 0, winreg.KEY_ALL_ACCESS)
            if enabled:
                if not app_path:
                    app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
            else:
                try:
                    winreg.DeleteValue(key, self.APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Windows Registry Autostart error: {e}")

    def is_autostart_enabled(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, self.APP_NAME)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
