# Build & Release Documentation

This guide provides instructions for building, running, and releasing **TikTok Live Auto Liker / Tapper** across **Windows**, **macOS**, and **Linux**.

---

## 1. Quick Start (Running from Source)

### Requirements:
- Python 3.10+ (Python 3.11 recommended)
- `pip`

### Step 1: Install Dependencies
```bash
# macOS / Linux
pip install -r requirements.txt

# Windows
pip install -r requirements.txt
```

### Step 2: Launch App
```bash
python tiktok_live_auto_liker_tapper.py
```

---

## 2. Standalone Local Packaging (`build.py`)

A single script handles packaging on all operating systems:

```bash
python build.py
```

### Operating System Specifics:

### 🍎 macOS
- **Requirements**: Xcode Command Line Tools (`xcode-select --install`)
- **Output**: `dist/TikTokLiveAutoLiker.app`
- **Create Distributable Zip**:
  ```bash
  cd dist
  zip -r -y TikTokLiveAutoLiker-macOS.zip TikTokLiveAutoLiker.app
  ```

### 🪟 Windows
- **Requirements**: Microsoft Edge WebView2 Runtime (installed by default on Windows 10/11)
- **Output**: `dist/TikTokLiveAutoLiker.exe`
- Standalone portable `.exe`, ready for distribution.

### 🐧 Linux
- **Requirements**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1-mesa-glx libegl1-mesa
  ```
- **Output**: `dist/TikTokLiveAutoLiker`
- **Create Distributable Tarball**:
  ```bash
  cd dist
  tar -czf TikTokLiveAutoLiker-Linux.tar.gz TikTokLiveAutoLiker
  ```

---

## 3. Automated GitHub Actions Release Workflow

The project uses `.github/workflows/build.yml` to automatically compile and release binaries for all 3 platforms whenever a tag is pushed.

### Workflow Pipeline:
```
git tag vX.Y.Z ───► git push origin --tags
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  Windows Runner    macOS Runner     Linux Runner
  (builds .exe)    (builds .zip)   (builds .tar.gz)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
               GitHub Actions Release
            (Publishes all 3 binaries)
```

### Release Procedure:
1. Update `APP_VERSION = "vX.Y.Z"` in `tiktok_live_auto_liker_tapper.py`.
2. Update `RELEASE_NOTES.md`.
3. Update release name in `.github/workflows/build.yml`.
4. Commit and tag:
   ```bash
   git add tiktok_live_auto_liker_tapper.py RELEASE_NOTES.md .github/workflows/build.yml
   git commit -m "chore: release vX.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main --tags
   ```
5. All three platform assets (`.exe`, `.zip`, `.tar.gz`) will be compiled in parallel and automatically published to GitHub Releases.
