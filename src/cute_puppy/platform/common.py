import os
import sys

def get_base_dir() -> str:
    """Returns the base directory of the application, handling PyInstaller frozen bundles."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
    else:
        # Returns root directory of repository containing src/ and assets/
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return src_dir

def get_asset_path(*paths) -> str:
    """Resolves runtime asset path safely for both dev and PyInstaller frozen executable modes."""
    base = get_base_dir()
    return os.path.join(base, "assets", *paths)

def get_version() -> str:
    """Reads VERSION file safely."""
    base = get_base_dir()
    v_path = os.path.join(base, "VERSION")
    if os.path.exists(v_path):
        try:
            with open(v_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "1.0.0"
