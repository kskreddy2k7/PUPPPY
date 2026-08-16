import os
import sys

class BasePlatform:
    def get_appdata_dir(self) -> str:
        raise NotImplementedError

    def register_autostart(self, app_path: str, enabled: bool):
        raise NotImplementedError

    def is_autostart_enabled(self) -> bool:
        raise NotImplementedError
