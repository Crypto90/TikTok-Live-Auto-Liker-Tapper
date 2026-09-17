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


def build_env() -> dict:
    """Environment for PyInstaller.

    A conda Python keeps native DLLs such as ffi.dll (needed by ctypes) and OpenSSL in Library/bin.
    PyInstaller only finds them when that folder is on PATH, as after `conda activate`; without it
    the exe builds fine but crashes at startup with "DLL load failed while importing _ctypes".
    """
    env = os.environ.copy()
    prefix = sys.base_prefix
    if sys.platform == "win32" and os.path.isdir(os.path.join(prefix, "conda-meta")):
        dirs = [prefix, os.path.join(prefix, "Library", "mingw-w64", "bin"), os.path.join(prefix, "Library", "usr", "bin"),
                os.path.join(prefix, "Library", "bin"), os.path.join(prefix, "Scripts")]
        env["PATH"] = os.pathsep.join(dirs + [env.get("PATH", "")])
    return env


def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, env=build_env())
    if res.returncode != 0:
        print(f"Error: Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)


def missing_python_dlls(exe_path: str) -> list:
    """DLLs that Python's own extension modules import, ship with this Python install, but are not in the exe."""
    import glob
    import pefile
    from PyInstaller.archive.readers import CArchiveReader

    bundled = {os.path.basename(name).lower() for name in CArchiveReader(exe_path).toc.keys()}
    prefix = sys.base_prefix
    search_dirs = [os.path.join(prefix, "DLLs"), os.path.join(prefix, "Library", "bin"), prefix]
    missing = []
    for module in ("_ctypes", "_ssl", "_hashlib", "_lzma", "_bz2", "pyexpat"):
        pyds = glob.glob(os.path.join(prefix, "DLLs", f"{module}*.pyd"))
        if not pyds:
            continue
        pe = pefile.PE(pyds[0], fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
        for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
            dll = entry.dll.decode("ascii", "ignore").lower()
            # System DLLs come from Windows itself; only the ones shipped with this Python must be bundled
            if dll not in bundled and any(os.path.exists(os.path.join(d, dll)) for d in search_dirs):
                missing.append(f"{module} needs {dll}")
    return missing


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
        f"--osx-bundle-identifier=com.crypto90.{APP_NAME.lower()}",
        "--add-data=icon.png:.",
        "--add-data=webview_engine.py:.",
        "--add-data=sync_manager.py:.",
        "--add-data=stats_manager.py:.",
        "--add-data=storage.py:.",
        "--add-data=app_logging.py:.",
        "--add-data=live_status.py:.",
        "--add-data=web_server.py:.",
        "--add-data=headless_runner.py:.",
    ]

    if os.path.exists("icon.icns"):
        cmd.append("--icon=icon.icns")
    elif os.path.exists("icon.png"):
        cmd.append("--icon=icon.png")

    cmd.append(MAIN_SCRIPT)
    run_cmd(cmd)

    # Apply deep ad-hoc codesignature to properly seal all nested frameworks
    print("Applying deep ad-hoc signature to bundle...")
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", f"dist/{APP_NAME}.app"], check=False)

    # Generate 1-click launcher helper script to bypass Gatekeeper quarantine
    launcher_path = f"dist/Open_{APP_NAME}.command"
    with open(launcher_path, "w") as f:
        f.write('#!/bin/bash\n')
        f.write('DIR="$(cd "$(dirname "$0")" && pwd)"\n')
        f.write(f'xattr -cr "$DIR/{APP_NAME}.app" 2>/dev/null\n')
        f.write(f'open "$DIR/{APP_NAME}.app"\n')
    os.chmod(launcher_path, 0o755)

    print(f"\n[SUCCESS] macOS app built: dist/{APP_NAME}.app")
    print(f"[SUCCESS] Launcher helper created: {launcher_path}")


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
        "--add-data=sync_manager.py:.",
        "--add-data=stats_manager.py:.",
        "--add-data=storage.py:.",
        "--add-data=app_logging.py:.",
        "--add-data=live_status.py:.",
        "--add-data=web_server.py:.",
        "--add-data=headless_runner.py:.",
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
        "--add-data=sync_manager.py;.",
        "--add-data=stats_manager.py;.",
        "--add-data=storage.py;.",
        "--add-data=app_logging.py;.",
        "--add-data=live_status.py;.",
        "--add-data=web_server.py;.",
        "--add-data=headless_runner.py;.",
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

    exe_path = os.path.join("dist", f"{APP_NAME}.exe")
    missing = missing_python_dlls(exe_path)
    if missing:
        print("\n[ERROR] The exe would crash at startup, required DLLs were not bundled:")
        for item in missing:
            print(f"  - {item}")
        sys.exit(1)
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
