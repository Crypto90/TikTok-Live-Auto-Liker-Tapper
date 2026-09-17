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

- 🧠 **Adaptive Rate Control**: Tunes the tap delay from server acknowledgments and pauses automatically while TikTok's like-frequency limit is active.
- 🎯 **Clean Hotkey Dispatching**: One bubbling `'L'` keypress per tap, matched to TikTok's 200ms shortcut throttle, with chat input safeguards.
- 🏃 **Full Speed in Background Tabs**: Streams in background tabs or a minimized window keep tapping at ~5 likes/s instead of being slowed to once per minute by the browser.
- 🚦 **"Likes Not Counting" Indicator & Alerts**: Every tab, grid card, PiP window and the web dashboard shows when TikTok limits or rejects likes, with optional desktop, Discord and Telegram alerts.
- 🔐 **Secured Headless Dashboard & Encrypted Cookie Sync**: Token login for the web dashboard, credentials that never leave the device, and TikTok session cookies synced only in encrypted form.
- 🖼️ **Isolated Picture-in-Picture (PiP)**: Compact, always-on-top floating window that strips out TikTok's chat, gift menus, and UI chrome to display **only the pure live video** with overlay controls.
- 🔲 **Multi-Stream Video Grid**: Monitor and like multiple live creators simultaneously in a responsive grid layout with per-card controls.
- 🔊 **Bidirectional Audio & Mute Sync**: Volume sliders and mute toggles stay in instantaneous lockstep across the Stream Top Bar, Favorites List, PiP Overlay, and Grid Cards.
- 🔔 **Multi-Channel Alerts**: Native desktop notifications, plus **Discord webhooks** and **Telegram bot** alerts when creators go live or reach major like milestones (10k, 25k, 50k, 100k, 250k, 500k, 1M).
- ⏱️ **Server-Verified Like Accounting**: Network sniffer intercepts `/webcast/room/like/` across `fetch` and `XMLHttpRequest`, reads the batched `count` from each request, and credits it only when the server answers `status_code === 0`.
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

### 🧠 Adaptive Rate Control
- **How TikTok counts likes**: The web player's `L` shortcut is throttled to one like per 200ms (about 5 likes/s). Taps are sent in batches: one `/webcast/room/like/` request per 15 taps, or after 500ms without a tap.
- **Defaults**: **200ms base delay + 5ms jitter** (~4.9 likes/s at ~100% confirmed). Delays below 200ms are clamped because the throttle merges those taps.
- **Feedback Controller**: Compares acknowledged likes to dispatched taps over 15-second windows (allowing for one unflushed batch) and backs off by `+10ms` when confirmation drops below 85%.
- **Frequency-Limit Pause**: When TikTok answers `status_code 4021043`, tapping pauses until `like_blocked_until_ms` passes. TikTok ignores taps during that block anyway. The stats bar shows `⏸️ TikTok limit, 1m 36s` with a countdown.
- **Stable Rate Readout**: Likes/s is measured between batch acknowledgments, so the display doesn't jump each time a batch of 15 arrives.
- **Full Speed in Background Tabs**: Chromium normally runs timers in hidden pages about once per second, and once per minute after 5 minutes. The app starts WebView2 and QtWebEngine with background throttling disabled (on macOS it turns off WebKit's hidden-page timer throttling and App Nap). Measured with a 200ms timer: hidden tab after 5 minutes 0.02 → 4.98 runs/s, minimized window 1.0 → 4.98 runs/s.
- **Watchdog Catch-Up**: If a tab still falls behind, the stats poll adds up to 3 taps per second, starting with one immediate tap that doesn't depend on page timers.

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
- **Likes Stopped Counting**: Alert when a stream's likes haven't counted for 3+ minutes (TikTok limit, rejected likes, or no confirmations, e.g. after being logged out), plus a follow-up when they count again.
- **One-Click Diagnostic Testing**: Test buttons in the settings dialog let you verify notification delivery instantly.

### ⏱️ 100% Server-Verified Like Counting
- **Dual Network Interception**: Hooks into `window.fetch` and `XMLHttpRequest.prototype.send` and reads the batch size from the JSON body TikTok posts to `/webcast/room/like/` (`{"count": N, ...}`).
- **Response Validation**: Credits likes only upon verified HTTP 200 responses with `status_code === 0`.
- **Delivery Status**: Shows ⏸️ **TikTok limit** (with countdown), ⚠️ **Likes rejected**, or ⚠️ **Not counting** (30+ taps without a confirmation) wherever likes are displayed.
- **Counts Survive Page Reloads**: Streams reload every 60 minutes to free memory. Like counts, session statistics and milestones continue from where they were instead of starting over at 0.
- **Bounded Delivery Metric**: Cleanly bounds the confirmation rate display between `0.0%` and `100.0%` while preserving 100% of real likes in cumulative statistics.

### 📊 Deep Analytics & Export
- **4 Key Performance Indicators (KPIs)**: Total Verified Likes, Total Taps Dispatched, Total Stream Watch Time, and Global Confirmed Delivery Rate.
- **Top Creators Leaderboard**: Creators ranked by verified likes delivered with session counts, delivery accuracy, and last-active timestamps.
- **14-Day Activity Bar Chart**: Visualizes daily likes delivered and watch time trends.
- **Stream Sessions Lifecycle**: Automatically records when streamers go live, likes delivered, and when they go offline.
- **TikTok Limit History**: Each session records how often and how long TikTok limited likes, plus the like delay used, so you can compare delay settings.
- **📥 CSV Data Export**: One-click download of full session history and raw analytics logs.

### ☁️ Multi-Device Cloud Synchronization
- Keep favorites, toggles (❤️), mute settings, and session statistics synchronized across **macOS**, **Windows gaming PCs**, and **Linux servers**:
  - **📁 Shared Folder / Cloud Drive**: Point to any folder inside your **Dropbox**, **Google Drive**, **OneDrive**, or **Syncthing** directory. Zero setup required!
  - **🌐 WebDAV**: Connect to **Nextcloud**, **ownCloud**, or **Fastmail**.
  - **⚡ REST API Server**: Self-hosted or centralized sync server with API key authorization.
- **🍪 Encrypted TikTok Session & Cookie Sync**: Synchronizes TikTok login cookies (`sessionid`) so headless Linux servers like under your personal account. Cookies are encrypted (AES-256-GCM, scrypt key) with a passphrase you enter on every device and are never synced without one. Signing out on one device signs out the others.
- **🔑 Credentials Stay Local**: Sync passwords, API keys, Discord webhooks and Telegram bot tokens are never written to the sync target.
- **Conflict-Free Merging**: Last-Write-Wins (LWW) resolution with deletion tombstones prevents deleted creators from reappearing.
- **Crash-Safe Local Files**: Favorites, settings, cookies and statistics are saved atomically with a backup copy, so a crash or power loss while saving can't wipe them.

### 🖥️ Native Browser Engine Architecture
- **macOS**: Native **Apple WebKit (`WKWebView`)** via `pyobjc-framework-WebKit` with hardware-accelerated H.264/HEVC/AAC video decoding and minimal CPU/memory footprint.
- **Windows**: **Microsoft Edge WebView2 (`qtwebview2`)** with low-memory Chromium flags.
- **Linux**: **`PyQt6-WebEngine`** with DocumentCreation codec shims for seamless TikTok Live player mounting.
- **Zero-Leak In-Page Engine**: Native JavaScript tapping loop executes directly in the DOM, eliminating IPC queue congestion and V8 heap growth. Floating heart animations are pruned automatically every 3 seconds.
- **Lightweight Live Detection**: Live status comes from one small TikTok API request per creator (~10 KB) instead of loading each creator's live page with video in a hidden browser. The page check only runs as a fallback.
- **Error Log**: Errors, crashes and engine warnings are written to `logs/autoliker.log` in the data folder. The **📄 Logs** button in the sidebar opens it; attach that file when reporting a problem.

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
The dashboard requires a login and listens on `127.0.0.1` by default. On startup the server prints a login link:
```
Web Dashboard: http://127.0.0.1:8080/#token=<access-token>
```
- The token is generated on first start and saved as `dashboard_token.txt` in the data folder. Set `TIKTOK_AUTOLIKER_TOKEN` or pass `--token` to choose your own.
- From another computer, use an SSH tunnel (`ssh -L 8080:127.0.0.1:8080 your-server`) and open the link locally.
- To listen on the network, start with `--host 0.0.0.0` and put an HTTPS reverse proxy in front before exposing it to the internet.

### 3. Deploy with Docker
```bash
cd server
docker compose up -d
docker logs tiktok-live-autoliker   # shows the dashboard login link
```
The compose file publishes the dashboard on `127.0.0.1:8080` of the host only.

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
4. Check **Sync TikTok login session & cookies** and enter a **cookie passphrase**. Use the same passphrase on every device; cookies are not synced without one.
5. Click **Test Connection**, then **Save & Apply**.
6. Using the REST sync server? Start it with an API key: `python sync_server.py --host 0.0.0.0 --api-key <secret>` (it refuses to listen on the network without one).

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
