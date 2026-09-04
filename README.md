[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

<a href="https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme">
  <img src="icon.png" width="200" height="200" align="center" alt="App Icon">
</a>

# TikTok Live Auto Liker / Tapper

A powerful, high-performance desktop application built with Python, PyQt6, and a cross-platform browser engine that automatically monitors your favorite TikTok creators and auto-taps (likes) their live streams in real-time.

Supports **macOS**, **Linux**, and **Windows**.

---

## 🚀 Features

- **Cross-Platform Native Browser Engine**:
  - **macOS**: Powered by native **Apple WebKit (`WKWebView`)** with hardware-accelerated H.264/HEVC/AAC video decoding, whisper-quiet CPU performance, and minimal memory usage.
  - **Windows**: Powered by **Microsoft Edge WebView2 (`qtwebview2`)** with low-memory optimizations.
  - **Linux**: Powered by **`PyQt6-WebEngine`** with DocumentCreation codec shims for seamless TikTok Live player mounting.
- **Zero-Leak In-Page Auto-Tapper Engine**: Likes are simulated natively inside the browser context, eliminating IPC queue congestions and V8 heap leaks (resolving Error 36 Out-Of-Memory crashes). Floating heart animations are pruned automatically every 3 seconds to keep memory flat.
- **Automated Live Stream Monitoring**: Quietly checks your favorite creators in the background using parallel worker threads and automatically opens their stream tabs as soon as they go live.
- **Advanced Real-Time Sorting**: Multi-criteria sorting for your favorites list with direction indicators (▲/▼):
  - **📡 Live Status**: Sorts live creators to the top by default.
  - **🔤 Name**: Alphabetical sorting (A-Z / Z-A).
  - **❤️ Auto-Tapper**: Sort by auto-tapper status (ON / OFF).
  - **🔇 Mute**: Sort by audio state (Unmuted / Muted).
  - In-memory avatar caching ensures lightning-fast re-sorting with zero disk I/O flicker.
- **Real-Time Monitoring Stats**: Bottom status bar displaying live statistics (`Monitoring X users │ Y live │ Z liking`) that update immediately upon heart toggles or status checks.
- **Per-User Stream Controls**:
  - **❤️ Heart Toggle**: Enable or disable auto-tapping per creator.
  - **🔊/🔇 Audio Mute Toggle**: Independently control stream audio for each creator.
- **Customizable Liking Rate**:
  - Adjust **Base Delay** (50ms – 500ms) and **Randomization** (0ms – 100ms) to simulate natural tapping speeds.
  - Quick **Reset** button to restore default speed settings.
- **Login & Explore Integration**: Integrated tabs to log into your TikTok account and explore live streams directly inside the application.
- **☁️ Multi-Device Synchronization**:
  - Keep all your favorites, auto-tapper toggles (❤️), audio states, and speed settings in sync between **macOS**, **Windows gaming PCs**, **secondary laptops**, and **Linux servers**.
  - **Shared Folder / Cloud Drive**: Zero-configuration sync using Dropbox, Google Drive, OneDrive, Syncthing, or local network shares.
- **WebDAV**: Remote cloud sync with Nextcloud, ownCloud, or Fastmail.
- **REST API / Central Sync Server**: Self-hosted or centralized sync server with API key authorization.
- **TikTok Login Session & Cookie Synchronization**: TikTok session cookies (`sessionid`, etc.) automatically synchronize across devices so that your remote Linux servers tap and like under your authenticated TikTok account!
- Conflict-free state merging with deletion tombstones ensures changes never overwrite each other.
- **🖥️ Headless Linux Server Mode & Web Dashboard**:
  - Run 24/7 on servers or VPS instances with no physical monitor required (supports virtual framebuffers via Xvfb).
  - Built-in modern, responsive dark-themed **Web Dashboard** (`http://server-ip:8080`) for remote stream monitoring, adding/removing creators, speed sliders, and live logs.
  - **Full Web-Based Cloud Sync Configuration**: Set up, test, and trigger cloud sync (Google Drive, WebDAV, REST) directly from the browser without touching terminal configs.
  - **In-Browser Cookie Management**: View active authentication status and paste/import TikTok session cookies directly in the web UI.
  - Ready-to-use **systemd** service and **Docker** container configs.
- **📊 100% Verified Like Counting & Live Analytics**:
  - **In-Page Server Confirmation**: Intercepts TikTok's internal `/webcast/room/like/` network requests and verifies each batch with `status_code === 0` from TikTok servers.
  - **Real-Time Floating Stats Bar**: Live watching displays real-time verified like counts (ticking up live!), likes/sec throughput, session duration timer, and delivery confirmation percentage.
  - **Dynamic Tab Badges**: Stream tab titles tick up dynamically as likes are confirmed (e.g. `❤️ LIVE: @kayceeedilla (❤️ 14,820)`).
  - **Stream Session Tracking**: Automatically logs every live stream session from start to finish with duration, confirmed likes sent, taps dispatched, and room growth.
  - **Analytics Dashboards (Desktop App & Web)**:
    - Top KPI metric cards: Total Verified Likes, Taps Dispatched, Watch Time, and Confirmation Rate.
    - 14-Day interactive activity timeline chart.
    - Top Creators Leaderboard ranked by likes given.
    - Searchable stream session history with one-click **CSV export**.
  - **Cross-Device Stats Sync**: Stream sessions and statistics automatically merge across your desktop PCs and 24/7 headless servers!
- **Modern Dark UI**: Sleek dark-mode interface with styled container boxes, horizontal-scroll prevention, and a pulsing status indicator when idle.

<img width="1372" height="832" alt="image" src="https://github.com/user-attachments/assets/2d662b62-e54f-42ca-a91d-2285641963c6" />

---

## 💻 Installation & Requirements

### 1. Clone the Repository
```bash
git clone https://github.com/Crypto90/TikTok-Live-Auto-Liker-Tapper.git
cd TikTok-Live-Auto-Liker-Tapper
```

### 2. Install Dependencies
Install the requirements using `pip`. Platform-specific dependencies (such as WebKit for macOS or WebView2 for Windows) will be resolved automatically:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python tiktok_live_auto_liker_tapper.py
```

---

## ☁️ Multi-Device Synchronization

To keep all your apps in sync across your Mac, Windows gaming PC, secondary laptop, and Linux servers:

1. In the application sidebar under **Data Management**, click **☁️ Cloud Sync**.
2. Check **Enable Automatic Cloud Sync**.
3. Choose your preferred sync method:
   - **📁 Shared Folder / Cloud Drive**: Point to any folder inside your **Dropbox**, **OneDrive**, **Google Drive**, or **Syncthing** directory. Zero setup required!
   - **🌐 WebDAV**: Enter your **Nextcloud** / **ownCloud** URL, username, and password.
   - **⚡ REST API Server**: Connect to a central sync server running `sync_server.py`.
4. Click **Test Connection**, then **Save & Apply** (or click **Sync Now** to immediately synchronize).

Any creator added, heart toggled, or speed adjusted on any device will automatically propagate to all your other computers!

---

## 🖥️ Headless Linux Server Mode & Web Dashboard

For 24/7 unmonitored liking on a home server, Raspberry Pi, or cloud VPS:

### Run Headless Directly
```bash
# On headless Linux without a physical display, run with xvfb-run:
xvfb-run -a python headless_runner.py --port 8080

# Or via the main app CLI flag:
xvfb-run -a python tiktok_live_auto_liker_tapper.py --headless --port 8080
```

### Access the Web Dashboard
Open your browser and navigate to:
```
http://<your-server-ip>:8080
```
- **Live Streams**: Real-time cards of creators currently streaming with live badges, tap rates, and one-click toggles.
- **Favorites Manager**: Add or remove creators, toggle auto-tapping (❤️) and mute (🔇).
- **Speed Rates**: Adjust Base Delay and Randomization sliders remotely.
- **Sync Now**: Trigger cloud sync with a single click.
- **Activity Logs**: Real-time terminal log console.

### Deploy with Docker
```bash
cd server
docker compose up -d
```

### Deploy with Systemd (Ubuntu / Debian / CentOS)
```bash
sudo cp server/tiktok-autoliker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tiktok-autoliker
```

---

## 📖 How to Use

1. **Launch the Application**: Start the app via `python tiktok_live_auto_liker_tapper.py` or run your compiled standalone binary.
2. **Log In (Optional)**: If prompted, log into your TikTok account via the built-in Login tab.
3. **Add Favorites**: Enter a TikTok username (e.g., `username` or `@username`) under **Favorites** and click **Add**.
4. **Configure Tapping & Audio**:
   - Click the **❤️ (Heart)** icon next to any user to enable/disable auto-tapping for their stream.
   - Click the **🔊/🔇 (Mute)** icon to toggle stream audio on or off.
5. **Sort & Organize**: Use the sort bar above the list (**Name**, **Live**, **Tapper**, **Mute**) to organize your favorites.
6. **Automated Monitoring & Tapping**: Sit back while the app monitors your list in the background. When an enabled favorite goes live, their stream opens in a tab and tapping begins automatically!
7. **Adjust Tapping Speed**: Customize base delay and randomization sliders under **Liking Settings** as desired.

---

## 🔨 Building Standalone Executable (.app / .exe / binary)

A unified cross-platform build script is provided:

```bash
python build.py
```

### Platform Output:
- **macOS**: Produces a standalone Application bundle with native high-res icon and a Gatekeeper bypass launcher:
  - `dist/TikTokLiveAutoLiker.app`
  - `dist/Open_TikTokLiveAutoLiker.command` ← **double-click this on first launch** to bypass Gatekeeper
- **Linux**: Produces a standalone Linux binary:
  `dist/TikTokLiveAutoLiker`
- **Windows**: Produces a standalone Windows executable:
  `dist/TikTokLiveAutoLiker.exe`

> **macOS users**: On first launch, use **`Open_TikTokLiveAutoLiker.command`** instead of the `.app` directly. This strips the macOS quarantine flag and opens the app. Subsequent launches of the `.app` will work normally.

---

## 💖 Support

If you find this project useful, you can support development via Ko-fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

---

## ⚖️ Disclaimer

This tool is for educational purposes only. Automated interaction with TikTok may violate their Terms of Service. Use at your own risk.
