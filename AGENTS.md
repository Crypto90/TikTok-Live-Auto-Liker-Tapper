# AGENTS.md — Developer & AI Agent Guide

Welcome to the **TikTok Live Auto Liker / Tapper** repository. This document serves as the single source of truth for AI agents (and human developers) working on this codebase across **macOS**, **Windows**, and **Linux**.

---

## 1. Architectural Overview

The application is built on **PyQt6** and features an operating-system-agnostic web engine layer designed in `webview_engine.py`.

```
┌─────────────────────────────────────────────────────────────┐
│                 PyQt6 Desktop Application                   │
│             (tiktok_live_auto_liker_tapper.py)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       User Interface & Tabs            LiveChecker Workers
     (PulsingTabBar, UserListItem)     (Status & Avatar Scans)
               │                               │
               └───────────────┬───────────────┘
                               │
            ┌──────────────────▼──────────────────┐
            │          UniversalWebView           │
            │        (webview_engine.py)          │
            └──────────────────┬──────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
      macOS                 Windows                 Linux
Apple WebKit (WKWebView)  Edge WebView2       PyQt6-WebEngine
(pyobjc-framework-WebKit) (qtwebview2)        (Chromium-based)
```

### Engine Selection Matrix (`UniversalWebView`):
1. **macOS (`darwin`)**: `MacWKWebViewWidget`
   - Uses Apple WebKit via `pyobjc-framework-WebKit`.
   - Uses private WebKit preferences (`_setMediaDataLoadsAutomatically_`, `_setRequiresUserGestureForVideoPlayback_`, `_setRequiresUserActionForVideoPlayback_`, `_setAllowsInlineMediaPlayback_`, `_setMediaSourceEnabled_`).
   - Uses desktop Safari User-Agent (`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15`) so TikTok feeds desktop H.264/AAC video streams.
   - Evaluates JS via `evaluateJavaScript_completionHandler_`.
2. **Windows (`win32`)**: `WindowsWebView2Widget`
   - Uses Microsoft Edge WebView2 via `qtwebview2`.
   - Passes low-memory chromium flags (`--disable-features=Translate`, `--disable-background-networking`, `--in-process-gpu`).
   - Evaluates JS via `ExecuteScriptAsync`.
3. **Linux (`linux`) & Fallback**: `QtWebEngineWidget`
   - Uses Chromium via `PyQt6.QtWebEngineWidgets`.
   - Injects codec shims at `DocumentCreation` to bypass browser-compatibility blocking.

---

## 2. Local Development & Testing Workflows

### Prerequisites by Operating System

#### macOS (Apple Silicon / Intel)
```bash
brew install python@3.11
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (PowerShell / Command Prompt)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
*Note: Ensure the Microsoft Edge WebView2 Runtime is installed (pre-installed on Windows 10/11).*

#### Linux (Ubuntu / Debian / Fedora)
```bash
sudo apt-get update
sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1-mesa-glx libegl1-mesa
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Running the Application from Source
```bash
python tiktok_live_auto_liker_tapper.py
```

### Headless Verification Commands (Automated Unit Checks)

#### 1. Test Live Detection with an Online Streamer:
```bash
python3 -c "
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from tiktok_live_auto_liker_tapper import CheckerWorker

app = QApplication(sys.argv)
worker = CheckerWorker()

def on_status(user, is_live, avatar, is_error):
    print(f'STATUS: user={user}, is_live={is_live}, avatar_len={len(avatar)}, error={is_error}')
    app.quit()

worker.status_checked.connect(on_status)
worker.check_user('kayceeedilla')
QTimer.singleShot(15000, app.quit)
app.exec()
"
```

#### 2. Test Offline Detection:
```bash
python3 -c "
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from tiktok_live_auto_liker_tapper import CheckerWorker

app = QApplication(sys.argv)
worker = CheckerWorker()

def on_status(user, is_live, avatar, is_error):
    print(f'OFFLINE CHECK: user={user}, is_live={is_live}, error={is_error}')
    assert is_live == False
    app.quit()

worker.status_checked.connect(on_status)
worker.check_user('tiktok')
QTimer.singleShot(15000, app.quit)
app.exec()
"
```

---

## 3. Local Standalone Build Workflow (`build.py`)

The project contains a unified packaging script, `build.py`, that detects the running operating system and builds the native standalone binary using PyInstaller.

```bash
python build.py
```

### Build Artifacts Produced:

| Host OS | Build Command | Output File(s) | How to Archive |
| :--- | :--- | :--- | :--- |
| **macOS** | `python3 build.py` | `dist/TikTokLiveAutoLiker.app` + `dist/Open_TikTokLiveAutoLiker.command` | `cd dist && zip -r -y TikTokLiveAutoLiker-macOS.zip TikTokLiveAutoLiker.app Open_TikTokLiveAutoLiker.command` |
| **Windows** | `python build.py` | `dist\TikTokLiveAutoLiker.exe` | Ready as standalone `.exe` (or zip) |
| **Linux** | `python3 build.py` | `dist/TikTokLiveAutoLiker` | `cd dist && tar -czf TikTokLiveAutoLiker-Linux.tar.gz TikTokLiveAutoLiker` |

### Icon Assets Handled by `build.py`:
- macOS uses `icon.icns` (multi-resolution bundle created via `sips` + `iconutil` from `icon.png`).
- Windows uses `icon.ico`.
- Linux uses `icon.png`.

---

## 4. GitHub Release & CI/CD Workflow

The repository uses `.github/workflows/build.yml` with a decoupled 2-stage architecture:
1. **Stage 1: Parallel Matrix Compilation (`build`)**
   - Runs concurrently on `windows-latest`, `macos-latest`, and `ubuntu-22.04` with `fail-fast: false`.
   - Generates executables and uploads them to GitHub Actions artifact storage.
2. **Stage 2: Unified Release Publisher (`release`)**
   - Runs on `ubuntu-latest` with `needs: build` and `if: startsWith(github.ref, 'refs/tags/v')`.
   - Requires top-level `permissions: contents: write`.
   - Downloads all 3 artifacts and publishes the GitHub Release with:
     - `TikTokLiveAutoLiker.exe` (Windows)
     - `TikTokLiveAutoLiker-macOS.zip` (macOS)
     - `TikTokLiveAutoLiker-Linux.tar.gz` (Linux)
     - Release notes populated from `RELEASE_NOTES.md`.

### Step-by-Step Version Bump & Release Procedure

When releasing a new version (e.g., `vX.Y.Z`):

1. **Bump Version in Code**:
   In `tiktok_live_auto_liker_tapper.py`:
   ```python
   APP_VERSION = "vX.Y.Z"
   ```
2. **Update Release Notes**:
   Edit `RELEASE_NOTES.md` with features, bug fixes, and download links.
3. **Update Release Name in CI Workflow**:
   In `.github/workflows/build.yml`:
   ```yaml
   name: "vX.Y.Z - <Your Release Title>"
   ```
4. **Test Locally**:
   Run `python3 tiktok_live_auto_liker_tapper.py` to confirm everything launches and functions properly.
5. **Commit and Tag**:
   ```bash
   git add tiktok_live_auto_liker_tapper.py RELEASE_NOTES.md .github/workflows/build.yml
   git commit -m "chore: bump version to vX.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```
6. **Push to GitHub**:
   ```bash
   git push origin main --tags
   ```
7. **Monitor the CI/CD Pipeline**:
   The workflow will automatically run, compile all 3 platforms, and attach the binaries to the GitHub Release.

---

## 5. Critical Architecture Rules & Gotchas

### 🚨 Gotcha 1: WebKit JavaScript Top-Level `return` Exception
- **Symptom**: Online streamers falsely show as "Offline"; avatar checks return `None`.
- **Root Cause**: In WebKit (`evaluateJavaScript_completionHandler_`), scripts execute as top-level program text. Writing `return (function() { ... })();` causes a fatal `SyntaxError: Return statements are only valid inside functions.`.
- **Rule**: NEVER include a top-level `return` statement in strings passed to `evaluate_js`. Always use standard self-executing expressions: `(function() { return { ... }; })()`.
- **Safeguard**: Both `MacWKWebViewWidget.evaluate_js` and `QtWebEngineWidget.evaluate_js` automatically strip leading `return ` prefixes.

### 🚨 Gotcha 2: Qt Tab Signal Blocking & Reordering
- **Symptom**: Spurious `currentChanged` signals trigger during setup, causing background tabs to start loading or audio to leak.
- **Rule**: Whenever programmatically inserting, removing, or reordering tabs in `self.tabs`, ALWAYS wrap the modifications with `self.tabs.blockSignals(True)` and `finally: self.tabs.blockSignals(False)`.

### 🚨 Gotcha 3: Tab Cleanup Order on Login (`_on_login_success`)
- **Symptom**: User gets stuck on a blank white page after login; "System Idle" tab disappears.
- **Root Cause**: `_update_waiting_tab()` checks if `login_webview` is present in `self.tabs`. If called before removing `login_webview`, `needs_waiting` evaluates to `False` and deletes `waiting_webview`.
- **Rule**: ALWAYS remove and clean up `self.login_webview` FIRST before calling `self._update_waiting_tab()`.

### 🚨 Gotcha 4: Explore Tab Lazy-Loading & Audio Muting
- **Symptom**: TikTok video sound plays on startup even when the user is on the System Idle tab.
- **Rule**: `explore_webview` must never load URLs on startup. It loads `https://www.tiktok.com/` only when the user explicitly activates the Explore tab. When the user switches away to another tab, `explore_webview.set_muted(True)` and `explore_webview.set_background_mode(True)` must be called immediately.

### 🚨 Gotcha 5: Memory Leak & Error 36 Mitigation
- **Rule 1 (In-Page Tapping Loop)**: Never use a high-frequency Python timer (`QTimer`) to send JS evaluation calls for tapping. Inject the in-page loop (`window.__tiktokStartTapper`) ONCE upon page load.
- **Rule 2 (DOM Cleanup)**: Background tabs must clean up DOM animations (like particles, gift effects) every 3 seconds to prevent Chromium/WebKit renderer memory leaks.
- **Rule 3 (Stream Recycling)**: Live streams open longer than 2 hours are recycled via `_recycle_if_stale()` to completely flush accumulated media buffers.

### 🚨 Gotcha 6: Vector Icons vs. System Emoji Fonts
- **Symptom**: Heart icons or buttons appear tiny (7px wide) or misaligned on macOS/Linux compared to Windows.
- **Rule**: Do NOT rely on system fonts for core UI action icons (like the heart toggle). Use `make_heart_icon(size, color)` which draws vector paths using `QPainterPath` and locks button sizes with `setFixedSize(28, 28)`.

### 🚨 Gotcha 7: macOS Gatekeeper Quarantine on Downloaded Binaries
- **Symptom**: After downloading and unzipping the macOS release, macOS shows *"TikTokLiveAutoLiker.app can't be opened because Apple cannot check it for malicious software"* or similar. User must click "Allow" twice in System Settings → Privacy & Security.
- **Root Cause**: macOS tags all files downloaded from the internet with the `com.apple.quarantine` extended attribute. Because the app is only **ad-hoc signed** (no paid Apple Developer ID), Gatekeeper rejects it on first open.
- **Build-level fix** (already applied in `build.py`):
  1. `--osx-bundle-identifier=com.crypto90.tiktokliveautoliker` gives the bundle a proper `CFBundleIdentifier`.
  2. `codesign --force --deep --sign -` re-seals all nested Qt frameworks after PyInstaller packs them.
  3. `Open_TikTokLiveAutoLiker.command` launcher is auto-generated and included in the zip — it runs `xattr -cr` to strip quarantine before opening the app.
- **Rule**: ALWAYS include `Open_TikTokLiveAutoLiker.command` in the macOS zip. The zip command is:
  ```bash
  zip -r -y TikTokLiveAutoLiker-macOS.zip TikTokLiveAutoLiker.app Open_TikTokLiveAutoLiker.command
  ```
- **User workaround** (if they don't use the launcher): `xattr -cr /path/to/TikTokLiveAutoLiker.app` in Terminal.
