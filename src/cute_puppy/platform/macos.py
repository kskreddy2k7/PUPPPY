import os
import sys

class MacOSPlatform:
    PLIST_LABEL = "com.cutepuppy.desktop"

    def get_appdata_dir(self) -> str:
        home = os.path.expanduser("~")
        target = os.path.join(home, "Library", "Application Support", "CutePuppy")
        os.makedirs(target, exist_ok=True)
        return target

    def _get_plist_path(self) -> str:
        home = os.path.expanduser("~")
        agents_dir = os.path.join(home, "Library", "LaunchAgents")
        os.makedirs(agents_dir, exist_ok=True)
        return os.path.join(agents_dir, f"{self.PLIST_LABEL}.plist")

    def register_autostart(self, app_path: str, enabled: bool):
        plist_path = self._get_plist_path()
        if enabled:
            if not app_path:
                app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{self.PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
            with open(plist_path, "w", encoding="utf-8") as f:
                f.write(plist_content)
        else:
            if os.path.exists(plist_path):
                os.remove(plist_path)

    def is_autostart_enabled(self) -> bool:
        return os.path.exists(self._get_plist_path())
