import sys
from platform_impl.base import BasePlatform

def get_platform() -> BasePlatform:
    if sys.platform == "win32":
        from platform_impl.windows import WindowsPlatform
        return WindowsPlatform()
    elif sys.platform == "darwin":
        from platform_impl.macos import MacOSPlatform
        return MacOSPlatform()
    else:
        from platform_impl.windows import WindowsPlatform
        return WindowsPlatform()
