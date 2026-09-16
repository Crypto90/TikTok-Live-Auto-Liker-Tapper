# 🚀 TikTok Live Auto Liker v1.2.2

Fixes the frozen like counter, keeps background streams tapping at full speed, and locks down the headless dashboard and cloud sync.

---

## 🌟 What's New in v1.2.2

### ❤️ Like Counting Fixed
- **Stats bar no longer stuck at 0**: A crash in the stats update kept `Verified`, `likes/s` and `Confirmed` frozen at their starting values.
- **Batches counted correctly**: TikTok sends likes in batches of up to 15. Each batch is now credited with its real size instead of 1.
- **Steady likes/s readout**: The rate no longer jumps every time a batch arrives.

### 🏃 Full Speed in Background Tabs
- Streams in background tabs or a minimized window were slowed by the browser to about 1 tap per second, and to about 1 per minute after 5 minutes. They now tap at full speed (measured: 0.02 → 4.98 timer runs per second).

### 🎯 Matched to TikTok's Limits
- TikTok's web player allows one like per 200ms via the `L` shortcut. New defaults: **200ms delay + 5ms jitter** (~4.9 likes/s at ~100% confirmed). Saved delays below 200ms are raised to 200ms.
- When TikTok temporarily blocks likes, tapping pauses until the block ends.

### 🚦 "Likes Not Counting" Indicator & Alerts
- ⏸️ **TikTok limit** (with countdown), ⚠️ **Likes rejected** and ⚠️ **Not counting** appear in the stats bar, tab title, grid cards, PiP window and web dashboard.
- Optional desktop, Discord and Telegram alert when a stream's likes stop counting for 3+ minutes, plus a note when they recover (Alerts & Webhooks settings).
- Session history and CSV export now show how often and how long TikTok limited likes, and the delay used.

### 🔐 Security
- **Web dashboard login**: The headless dashboard now requires an access token and listens on `127.0.0.1` by default. The login link is printed at startup; use `--host 0.0.0.0` to allow other machines (preferably behind HTTPS).
- **Encrypted cookie sync**: TikTok session cookies are synced only when encrypted with a **cookie passphrase**. Enter the same passphrase on every device in Cloud Sync settings. Without one, cookies stay on the device.
- **Credentials stay local**: Sync passwords, API keys, Discord webhooks and Telegram tokens are no longer written to the sync folder or server. Existing sync files are cleaned on the next sync.
- **Sign-out syncs**: Signing out on one device now signs out the others instead of being undone.
- **Sync server**: `sync_server.py` refuses to listen on the network without an API key.

### 🛠️ Also Fixed
- `tiktok_live_auto_liker_tapper.py --headless` no longer exits with an argument error.
- The "Sync TikTok Session Cookies" switch is now respected.
- Web dashboard activity log shows messages again.

---

## ⚠️ Before You Update

- **Update all devices that use Cloud Sync.** Older versions don't understand encrypted cookies and would upload credentials again.
- **Set a cookie passphrase** on each device if you sync TikTok cookies.
- **Headless server users**: Log in with the link from the console (`docker logs` / `journalctl`). Docker and systemd now publish the dashboard on localhost only; see the README to reach it remotely.

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Download the archive or executable for your platform and replace your previous file. Your favorites, settings, cookies and statistics carry over.

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_122)
