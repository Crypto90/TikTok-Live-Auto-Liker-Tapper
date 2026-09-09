# 🚀 TikTok Live Auto Liker v1.1.9

A stability and polish release delivering **full bidirectional synchronization of mute and volume states across all UI surfaces** and resolving a **desktop notification testing crash**.

---

## 🌟 What's New in v1.1.9

### 🔊 Bidirectional Mute & Volume Synchronization
- **Complete Multi-Surface Harmony**: Adjusting volume or toggling mute on a streamer's top bar now instantly updates their speaker icon (`🔊` / `🔇`) in the left favorites list, and vice versa.
- **PiP & Grid Sync**: Volume sliders in Picture-in-Picture (PiP) and Multi-Stream Grid cards remain in lockstep with the active tab and the favorites list.
- **Accurate Tab Initialization**: When opening a streamer's tab who is set to muted, the stream starts strictly at 0% volume while remembering their previous volume level, ensuring that unmuting cleanly restores the desired listening level.
- **Dynamic Re-sorting**: Mute state changes immediately trigger list re-sorting when sorting favorites by mute status.

### 🔔 Desktop Notification Test Fix & macOS Fallback
- **Crash Resolution**: Resolved a `TypeError` when clicking **"Test Desktop Notification"** inside the Alerts & Webhooks settings dialog.
- **Instant Test Delivery**: Test notifications now display immediately without requiring pre-saved settings changes.
- **Native macOS Fallback**: Added a native AppleScript (`osascript`) notification fallback on macOS in the event `QSystemTrayIcon` is temporarily unavailable.

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All existing configurations (`favorites.json`, `settings.json`, `cookies.json`, `sync_config.json`, `stats.json`) are 100% compatible and will carry over seamlessly!

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_119)
