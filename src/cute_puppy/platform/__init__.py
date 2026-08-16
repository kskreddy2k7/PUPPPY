import sys

def get_platform():
    if sys.platform == "win32":
        from cute_puppy.platform.windows import WindowsPlatform
        return WindowsPlatform()
    elif sys.platform == "darwin":
        from cute_puppy.platform.macos import MacOSPlatform
        return MacOSPlatform()
    else:
        from cute_puppy.platform.windows import WindowsPlatform
        return WindowsPlatform()
