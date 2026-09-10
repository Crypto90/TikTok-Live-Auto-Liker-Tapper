<div align="center">
  <img src="screenshots/header_banner.jpg" alt="TikTok Live Auto Liker / Tapper Banner" width="100%" style="border-radius: 12px; margin-bottom: 16px;">

  [![Release](https://img.shields.io/github/v/release/Crypto90/TikTok-Live-Auto-Liker-Tapper?style=for-the-badge&color=fe2c55)](https://github.com/Crypto90/TikTok-Live-Auto-Liker-Tapper/releases)
  [![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-25f4ee?style=for-the-badge)](https://github.com/Crypto90/TikTok-Live-Auto-Liker-Tapper)
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![License](https://img.shields.io/github/license/Crypto90/TikTok-Live-Auto-Liker-Tapper?style=for-the-badge&color=white)](LICENSE)
  [![ko-fi](https://img.shields.io/badge/Support-Ko--Fi-ff5e5b?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

  <br>

  <h1>⚡ TikTok Live Auto Liker / Tapper ⚡</h1>

  <p><b>High-Performance Desktop Application (macOS, Windows, Linux) & 24/7 Headless Linux Server</b></p>
  <p>Smart Adaptive Auto-Throttling • 90%+ Server Confirmation • Isolated Picture-in-Picture • Multi-Stream Grid • Multi-Device Cloud Sync</p>
</div>

---

## 🌟 Highlights & Newest Capabilities

- 🧠 **Smart Adaptive Auto-Throttling**: Closed-loop PID-style rate optimizer automatically monitors TikTok's client/server debounce and self-tunes delays in real time to guarantee **90%+ server confirmation rates**.
- 🎯 **Clean Hotkey Dispatching**: Replaced dual-event collisions with native, bubbling `'L'` keypresses matching TikTok's desktop player architecture with built-in chat input safeguards.
- 🖼️ **Isolated Picture-in-Picture (PiP)**: Compact, always-on-top floating window that strips out TikTok's chat, gift menus, and UI chrome to display **only the pure live video** with overlay controls.
- 🔲 **Multi-Stream Video Grid**: Monitor and like multiple live creators simultaneously in a responsive grid layout with per-card controls.
- 🔊 **Bidirectional Audio & Mute Sync**: Volume sliders and mute toggles stay in instantaneous lockstep across the Stream Top Bar, Favorites List, PiP Overlay, and Grid Cards.
- 🔔 **Multi-Channel Alerts**: Native desktop notifications, plus **Discord webhooks** and **Telegram bot** alerts when creators go live or reach major like milestones (10k, 25k, 50k, 100k, 250k, 500k, 1M).
- ⏱️ **100% Server-Verified Like Accounting**: Dual-layer network sniffer intercepts HTTP `/webcast/room/like` and `/webcast/room/digg` across `fetch` and `XMLHttpRequest`, confirming `status_code === 0` before crediting.
- ☁️ **Multi-Device Cloud & Cookie Sync**: Synchronize favorites, audio settings, and authenticated TikTok login cookies across macOS, Windows, and Linux via Shared Folders (Google Drive / Dropbox / OneDrive), WebDAV (Nextcloud), or REST API.
- 🖥️ **Tri-Platform Native Web Engines**: Apple WebKit (`WKWebView`) on macOS, Microsoft Edge WebView2 on Windows, and QtWebEngine Chromium on Linux.

---

## 📸 Interface Previews

### 🖥️ PyQt6 Desktop Application (macOS, Windows, Linux)

<div align="center">
  <img src="screenshots/desktop_main_window.png" alt="Desktop Application Main Window" width="100%" style="border-radius: 10px; border: 1px solid #282e3d; margin-bottom: 16px;">
  <p><i>Desktop application featuring the live stream player, glassmorphism verified stats bar, dynamic pulsing tab badges, creator favorites sorting, and volume controls.</i></p>
</div>

<br>

<div align="center">
  <table>
    <tr>
      <td width="55%" align="center">
        <b>📊 Stream Analytics & Verified Likes Leaderboard</b>
        <br><br>
        <img src="screenshots/desktop_analytics.png" alt="Desktop Analytics & Leaderboard" width="100%" style="border-radius: 8px; border: 1px solid #282e3d;">
        <br>
        <small><i>KPI cards, ranked creator leaderboard, session logs & CSV export</i></small>
      </td>
      <td width="45%" align="center">
        <b>☁️ Multi-Device Cloud & Cookie Sync</b>
        <br><br>
        <img src="screenshots/desktop_cloud_sync.png" alt="Desktop Cloud Sync Settings" width="100%" style="border-radius: 8px; border: 1px solid #282e3d;">
        <br>
        <small><i>Google Drive, WebDAV, REST sync & TikTok session cookies</i></small>
      </td>
    </tr>
  </table>
</div>

---

### 🌐 24/7 Headless Linux Server & Responsive Web Dashboard

Run unmonitored on home servers, Raspberry Pi, or cloud VPS instances with a sleek dark-mode browser dashboard on `http://server-ip:8080`.

<div align="center">
  <img src="screenshots/web_dashboard_active_streams.png" alt="Web Dashboard Active Streams" width="100%" style="border-radius: 10px; border: 1px solid #282e3d; margin-bottom: 16px;">
  <p><i>Tab 1 — <b>Active Streams</b>: Live throughput rates, verified like batches, elapsed timers, and stream controls.</i></p>
</div>

<br>

<div align="center">
  <img src="screenshots/web_dashboard_analytics.png" alt="Web Dashboard Analytics" width="100%" style="border-radius: 10px; border: 1px solid #282e3d; margin-bottom: 16px;">
  <p><i>Tab 4 — <b>Analytics & Stats</b>: 14-day interactive SVG activity bar chart, top creators leaderboard, and session history.</i></p>
</div>

<br>

<div align="center">
  <img src="screenshots/web_dashboard_cloud_sync.png" alt="Web Dashboard Cloud Sync & Cookie Manager" width="100%" style="border-radius: 10px; border: 1px solid #282e3d; margin-bottom: 16px;">
  <p><i>Tab 3 — <b>Settings & Sync</b>: In-browser cloud sync configuration, connection diagnostics, and authenticated TikTok cookie manager.</i></p>
</div>

---

## 🚀 In-Depth Feature Breakdown

### 🧠 Smart Adaptive Auto-Throttling (90%+ Confirmation Rate)
- **Closed-Loop Feedback Controller**: Evaluates incoming server acknowledgments against dispatched taps every 20 taps.
- **Dynamic Throttle Backoff**: When network congestion or TikTok's client debounce drops confirmation below 78%, base delay smoothly backs off by `+15ms` (up to 260ms max).
- **Intelligent Speed Probing**: When delivery is flawless (≥90%), the engine gently probes faster by `-5ms` (down to 130ms min), finding the maximum like rate TikTok will accept.
- **Sweet-Spot Defaults**: Defaults to **165ms Base Delay + 35ms Jitter** (~182ms interval), precisely respecting TikTok's ~180ms client debounce window.
- **Live Latency Feedback**: Displays real-time adaptive speed directly inside the stats bar (e.g. `📶 98.4% Confirmed (165ms)`).
- **Debounce-Respecting Bursts**: Background and minimized tabs use micro-spaced catch-up bursts (`Math.max(160, baseDelay)` ms) rather than instantaneous zero-delay floods.

### 🖼️ Video-Only Picture-in-Picture (PiP) Window
- **Always-on-Top Floating Window**: Detaches any active stream into a floating, resizable mini-player.
- **Video Element Isolation**: Injects CSS/JS rules to hide chat feeds, gift menus, top navigation headers, and recommendation sidebars, leaving **only the pure video feed**.
- **Glassmorphism Overlay**: Hovering reveals live verified likes count (`❤️ 14,250`), mute toggle (`🔊`/`🔇`), volume slider, and one-click dock-back button.
- **Seamless State Restoration**: Closing or docking back cleanly restores the full TikTok web interface without reloading or interrupting video playback.

### 🔲 Multi-Stream Video Grid (Multi-View)
- **Simultaneous Multi-Live Monitoring**: Watch and like up to 4+ live creators concurrently in an adaptive multi-view grid.
- **Independent Card Controls**: Each grid card features its own volume slider, mute toggle, like count indicator, and auto-tapper on/off switch.

### 🔊 Bidirectional Audio & Mute Synchronization
- **Universal Synchronization**: Changing volume or mute on a streamer's top bar instantly reflects on their speaker icon (`🔊` / `🔇`) in the favorites list, and vice versa.
- **PiP & Grid Alignment**: PiP window and Multi-Stream Grid cards remain in lockstep with the active tab.
- **Smart Muted Tab Initialization**: Streams opened while muted initialize at 0% volume while remembering your preferred volume setting, so unmuting cleanly restores the desired level.

### 🔔 Multi-Channel Alerts (Desktop, Discord & Telegram)
- **Native OS Notifications**: Native notification toasts on macOS, Windows, and Linux (with native AppleScript `osascript` fallback on macOS).
- **Discord Webhook Alerts**: Formatted rich embeds sent to your Discord channel when a favorited streamer goes live or achieves milestone likes.
- **Telegram Bot Alerts**: Instant messages delivered directly to your Telegram chat or group.
- **Like Milestones**: Configurable alerts for major achievements: **10k, 25k, 50k, 100k, 250k, 500k, and 1,000,000 likes**.
- **One-Click Diagnostic Testing**: Test buttons in the settings dialog let you verify notification delivery instantly.

### ⏱️ 100% Server-Verified Like Counting
- **Dual Network Interception**: Hooks into `window.fetch` and `XMLHttpRequest.prototype.send` to capture exact outgoing batch sizes (`count=...`).
- **Response Validation**: Credits likes only upon verified HTTP 200 responses with `status_code === 0`.
- **Bounded Delivery Metric**: Cleanly bounds the confirmation rate display between `0.0%` and `100.0%` while preserving 100% of real likes in cumulative statistics.

### 📊 Deep Analytics & Export
- **4 Key Performance Indicators (KPIs)**: Total Verified Likes, Total Taps Dispatched, Total Stream Watch Time, and Global Confirmed Delivery Rate.
- **Top Creators Leaderboard**: Creators ranked by verified likes delivered with session counts, delivery accuracy, and last-active timestamps.
- **14-Day Activity Bar Chart**: Visualizes daily likes delivered and watch time trends.
- **Stream Sessions Lifecycle**: Automatically records when streamers go live, likes delivered, and when they go offline.
- **📥 CSV Data Export**: One-click download of full session history and raw analytics logs.

### ☁️ Multi-Device Cloud Synchronization
- Keep favorites, toggles (❤️), mute settings, and session statistics synchronized across **macOS**, **Windows gaming PCs**, and **Linux servers**:
  - **📁 Shared Folder / Cloud Drive**: Point to any folder inside your **Dropbox**, **Google Drive**, **OneDrive**, or **Syncthing** directory. Zero setup required!
  - **🌐 WebDAV**: Connect to **Nextcloud**, **ownCloud**, or **Fastmail**.
  - **⚡ REST API Server**: Self-hosted or centralized sync server with API key authorization.
- **🍪 Cross-Device TikTok Session & Cookie Sync**: Synchronizes authenticated TikTok login cookies (`sessionid`) so headless Linux servers like under your personal account.
- **Conflict-Free Merging**: Last-Write-Wins (LWW) resolution with deletion tombstones prevents deleted creators from reappearing.

### 🖥️ Native Browser Engine Architecture
- **macOS**: Native **Apple WebKit (`WKWebView`)** via `pyobjc-framework-WebKit` with hardware-accelerated H.264/HEVC/AAC video decoding and minimal CPU/memory footprint.
- **Windows**: **Microsoft Edge WebView2 (`qtwebview2`)** with low-memory Chromium flags.
- **Linux**: **`PyQt6-WebEngine`** with DocumentCreation codec shims for seamless TikTok Live player mounting.
- **Zero-Leak In-Page Engine**: Native JavaScript tapping loop executes directly in the DOM, eliminating IPC queue congestion and V8 heap growth. Floating heart animations are pruned automatically every 3 seconds.

---

## 💻 Installation & Quick Start

### Option A: Download Pre-Compiled Standalone Binaries (Recommended)

Grab the latest standalone package from the **[GitHub Releases](https://github.com/Crypto90/TikTok-Live-Auto-Liker-Tapper/releases)** page:

- **Windows**: `TikTokLiveAutoLiker.exe` (Ready to run, no installation required)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (Includes `TikTokLiveAutoLiker.app` + `Open_TikTokLiveAutoLiker.command` launcher to bypass Gatekeeper)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone 64-bit binary)

> [!TIP]
> **macOS Users**: Because the app is ad-hoc signed, macOS Gatekeeper may show a quarantine prompt on first open. Simply double-click the included **`Open_TikTokLiveAutoLiker.command`** launcher to strip the quarantine attribute and launch immediately.

---

### Option B: Run from Source

#### 1. Clone the Repository
```bash
git clone https://github.com/Crypto90/TikTok-Live-Auto-Liker-Tapper.git
cd TikTok-Live-Auto-Liker-Tapper
```

#### 2. Install Dependencies
```bash
# macOS / Linux:
pip install -r requirements.txt

# Windows (PowerShell):
python -m pip install -r requirements.txt
```
*Platform-specific web engine bindings (WebKit on macOS, WebView2 on Windows) are resolved automatically.*

#### 3. Launch the Application
```bash
python tiktok_live_auto_liker_tapper.py
```

---

## 🖥️ Headless Linux Server Mode (24/7 Automation)

For unmonitored liking on a home server, Raspberry Pi, or cloud VPS without a physical display:

### 1. Run with Virtual Framebuffer (Xvfb)
```bash
# Direct runner:
xvfb-run -a python headless_runner.py --port 8080

# Or via main app CLI flag:
xvfb-run -a python tiktok_live_auto_liker_tapper.py --headless --port 8080
```

### 2. Access the Web Dashboard
Open your browser and navigate to:
```
http://<your-server-ip>:8080
```

### 3. Deploy with Docker
```bash
cd server
docker compose up -d
```

### 4. Deploy with Systemd (Ubuntu / Debian / CentOS)
```bash
sudo cp server/tiktok-autoliker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tiktok-autoliker
```

---

## ☁️ Multi-Device Cloud Sync Setup

1. In the desktop sidebar under **Data Management**, click **☁️ Cloud Sync** (or visit **Settings & Sync** in the Web Dashboard).
2. Check **Enable Automatic Cloud Sync**.
3. Choose your sync provider:
   - **📁 Shared Folder**: Select a folder inside Google Drive, Dropbox, OneDrive, or Syncthing.
   - **🌐 WebDAV**: Enter your Nextcloud / ownCloud server URL, username, and app password.
   - **⚡ REST API**: Enter your central sync server URL and API key.
4. Check **Sync TikTok login session & cookies** to enable authenticated headless liking.
5. Click **Test Connection**, then **Save & Apply**.

---

## 🔔 Discord & Telegram Notifications Setup

1. In the desktop sidebar under **Data Management**, click **🔔 Alerts & Webhooks**.
2. **Desktop Toasts**: Check **Enable Native OS Notifications** to receive desktop banners.
3. **Discord Integration**: Check **Enable Discord Channel Alerts** and paste your Discord Webhook URL.
4. **Telegram Integration**: Check **Enable Telegram Bot Alerts**, enter your Bot Token and Chat ID.
5. Click **Test Desktop Notification**, **Test Discord**, or **Test Telegram** to confirm delivery.
6. Click **Save & Close**.

---

## 🔨 Building Standalone Executables (`build.py`)

The repository includes a unified cross-platform build script:

```bash
python build.py
```

### Artifacts Produced:
| Host OS | Output File(s) | Description |
| :--- | :--- | :--- |
| **macOS** | `dist/TikTokLiveAutoLiker.app` + `dist/Open_TikTokLiveAutoLiker.command` | Universal/native macOS bundle with Gatekeeper launcher |
| **Windows** | `dist\TikTokLiveAutoLiker.exe` | Single-file Windows executable |
| **Linux** | `dist/TikTokLiveAutoLiker` | Standalone 64-bit Linux binary |

---

## 💖 Support Development

If you enjoy this project and find it helpful, you can support ongoing development via Ko-fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

---

## ⚖️ Disclaimer

This application is developed strictly for educational, testing, and research purposes. Automated interaction with TikTok may violate their Terms of Service. Please use responsibly and respect creator communities.
