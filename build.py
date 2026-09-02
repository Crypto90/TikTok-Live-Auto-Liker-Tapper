#!/usr/bin/env python3
"""Cross-platform build script for TikTok Live Auto Liker / Tapper.

Builds standalone executables / app bundles using PyInstaller for:
- macOS: Standalone .app bundle (with icon.icns)
- Linux: Standalone binary executable
- Windows: Standalone .exe (with icon.ico and WebView2 libraries)
"""

import os
import sys
import shutil
import subprocess

APP_NAME = "TikTokLiveAutoLiker"
MAIN_SCRIPT = "tiktok_live_auto_liker_tapper.py"


def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Error: Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)


def clean():
    print("Cleaning build and dist directories...")
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    for spec in [f"{APP_NAME}.spec"]:
        if os.path.exists(spec):
            os.remove(spec)


def build_macos():
    print("Building for macOS...")
    # Generate icon.icns if not present
    if not os.path.exists("icon.icns") and os.path.exists("icon.png"):
        print("Generating icon.icns from icon.png...")
        os.makedirs("icon.iconset", exist_ok=True)
        sizes = [16, 32, 64, 128, 256, 512]
        for s in sizes:
            subprocess.run(["sips", "-z", str(s), str(s), "icon.png", "--out", f"icon.iconset/icon_{s}x{s}.png"], capture_output=True)
            if s * 2 <= 1024:
                subprocess.run(["sips", "-z", str(s*2), str(s*2), "icon.png", "--out", f"icon.iconset/icon_{s}x{s}@2x.png"], capture_output=True)
        subprocess.run(["iconutil", "-c", "icns", "icon.iconset", "-o", "icon.icns"], capture_output=True)
        shutil.rmtree("icon.iconset", ignore_errors=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--windowed",
        "--clean",
        f"--name={APP_NAME}",
        "--add-data=icon.png:.",
        "--add-data=webview_engine.py:.",
    ]

    if os.path.exists("icon.icns"):
        cmd.append("--icon=icon.icns")
    elif os.path.exists("icon.png"):
        cmd.append("--icon=icon.png")

    cmd.append(MAIN_SCRIPT)
    run_cmd(cmd)
    print(f"\n[SUCCESS] macOS app built: dist/{APP_NAME}.app")


def build_linux():
    print("Building for Linux...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--name={APP_NAME}",
        "--add-data=icon.png:.",
        "--add-data=webview_engine.py:.",
    ]

    if os.path.exists("icon.png"):
        cmd.append("--icon=icon.png")

    cmd.append(MAIN_SCRIPT)
    run_cmd(cmd)
    print(f"\n[SUCCESS] Linux binary built: dist/{APP_NAME}")


def build_windows():
    print("Building for Windows...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--name={APP_NAME}",
        "--add-data=icon.png;.",
        "--add-data=webview_engine.py;.",
    ]

    # Include qtwebview2 libs if available
    try:
        import qtwebview2
        qtlib = os.path.join(os.path.dirname(qtwebview2.__file__), "lib")
        if os.path.exists(qtlib):
            cmd.append(f"--add-data={qtlib};lib")
    except ImportError:
        pass

    if os.path.exists("icon.ico"):
        cmd.append("--icon=icon.ico")
    elif os.path.exists("icon.png"):
        cmd.append("--icon=icon.png")

    cmd.append(MAIN_SCRIPT)
    run_cmd(cmd)
    print(f"\n[SUCCESS] Windows executable built: dist/{APP_NAME}.exe")


def main():
    clean()
    if sys.platform == "darwin":
        build_macos()
    elif sys.platform.startswith("linux"):
        build_linux()
    elif sys.platform == "win32":
        build_windows()
    else:
        print(f"Unknown platform: {sys.platform}")
        sys.exit(1)


if __name__ == "__main__":
    main()
