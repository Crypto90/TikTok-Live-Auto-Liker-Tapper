# 🚀 TikTok Live Auto Liker v1.1.3

A major feature update introducing **100% Server-Verified Like Counting**, **Live In-App Real-Time Ticking Counters**, **Stream Session Tracking & History**, **Analytics & Leaderboard Dashboards** (Desktop & Headless Web), and **Multi-Device History Synchronization**.

---

## 🌟 What's New in v1.1.3

### 🎯 100% Server-Verified Like Counting & Interception
Say goodbye to estimated or client-only click approximations! The engine now intercepts and inspects every outgoing HTTP request and TikTok server response at the network layer:
- **Dual API Interception**: Intercepts both `window.fetch` and `XMLHttpRequest` targeting `/webcast/room/like` and `/webcast/room/digg`.
- **Response Validation**: Parses TikTok server payloads, strictly verifying `status_code === 0` and extracting exact confirmed like batches (`count=X`).
- **Mathematical Accuracy**: Distinguishes between local dispatched taps and confirmed server acknowledgments, ensuring that all charts, session logs, and statistics reflect true, confirmed likes delivered to the creator.

### ⏱️ Live Real-Time Floating Stats Bar
When watching a live stream in the desktop app or monitoring via the web dashboard:
- **Live Counter Bar**: A sleek glassmorphism floating overlay above the stream displays real-time metrics:
  - ❤️ **Verified Likes**: Live ticking counter updating in real time as server confirmations arrive.
  - ⚡ **Rate**: Current live throughput (`likes/second`).
  - ⏱️ **Session Duration**: Active watch time timer (`mm:ss` / `hh:mm:ss`).
  - 📶 **Confirmed %**: Real-time delivery acknowledgment ratio.
- **Dynamic Tab Titles**: Live tabs now update dynamically with stream status and verified like counts (e.g., `❤️ LIVE: @streamer (❤️ 1,420)`).

### 📈 Comprehensive Stream Session Tracking
- **Automatic Lifecycle Tracking**: Tracks exactly when a creator went live, when tapping began, total watch time duration, total likes delivered, and when the streamer went offline.
- **Persistent Storage**: All session logs are preserved locally in `stats.json` with conflict-free UUID identifiers.
- **Multi-Device Session Sync**: Automatically syncs completed stream histories and statistics across all your desktop PCs and headless Linux servers via Cloud Sync.

### 📊 Beautiful Analytics & Leaderboard Dashboards
Gain deep insights into your tapping activity across both platforms:
- **PyQt6 Desktop App**:
  - Open via the new **`📊 Analytics & Stats`** button in the sidebar.
  - 4 High-impact KPI cards: Total Verified Likes, Total Taps Dispatched, Total Stream Watch Time, and Global Delivery Ratio.
  - **Top Creators Leaderboard**: Ranked table showing your most-supported streamers, total sessions, verified likes, and total watch time.
  - **Stream Sessions History**: Detailed, filterable table of past sessions with timestamps, durations, and verified like counts.
  - **📥 Export CSV**: Export full session history and raw analytics data to CSV for external analysis or archiving.
- **Headless Server Web Dashboard**:
  - Dedicated **`📊 Analytics & Stats`** tab on `http://server-ip:8080`.
  - Responsive KPI stat cards, interactive 14-day daily SVG activity bar chart, ranked creator leaderboard, session table with search filtering, and one-click CSV export.
  - Active Stream cards in Tab 1 now feature live verified like badges, rate counters, and duration timers.

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All existing configurations (`favorites.json`, `settings.json`, `cookies.json`, `sync_config.json`) are 100% compatible and will carry over seamlessly!

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_113)
