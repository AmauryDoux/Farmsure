"""
FarmSure – Crop Insurance Portal
Entry point: installs dependencies if needed, then launches the app.
"""

import subprocess
import sys


def ensure_deps():
    missing = []
    for pkg, import_name in [("customtkinter", "customtkinter"), ("Pillow", "PIL"), ("psycopg2-binary", "psycopg2")]:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing: {', '.join(missing)} …")
        # Try normal install first; fall back to --break-system-packages for
        # Homebrew-managed Python on macOS which blocks global pip installs.
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + missing)
        except subprocess.CalledProcessError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install",
                 "--break-system-packages"] + missing)


if __name__ == "__main__":
    ensure_deps()
    from app import FarmerInsuranceApp
    FarmerInsuranceApp().run()
