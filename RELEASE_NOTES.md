# 🚀 TikTok Live Auto Liker v1.2.3

Like counts that survive the hourly stream reload, faster and lighter live detection, crash-safe saving, and an error log.

---

## 🌟 What's New in v1.2.3

### ❤️ Like Counts No Longer Reset Every Hour
- Streams reload every 60 minutes to free memory (and when you press refresh). Previously the like counter started over at 0 each time, session statistics only kept the highest single hour, and milestones like 25k or 50k could be missed on long streams.
- Counts, session statistics, leaderboard, CSV export and milestones now continue across reloads. Example: two hours with 17,000 likes each now show 34,000 instead of 17,000.

### ⚡ Faster, Lighter Live Detection
- Live status now comes from one small TikTok request per creator (~10 KB, well under a second) instead of loading every creator's live page with video in hidden browsers.
- Less CPU, memory and data use, especially with many favorites. The previous page check remains as an automatic fallback.

### 💾 Crash-Safe Saving
- Favorites, settings, cookies and statistics are saved atomically with a backup copy. A crash or power loss while saving can no longer leave you with an empty favorites list.

### 📄 Error Log
- Errors, crashes and engine warnings are now written to `logs/autoliker.log` in the app's data folder. Open it with the new **📄 Logs** button in the sidebar and attach it when reporting a problem.

### 🖥️ Headless Server
- Web dashboard actions now run safely on the app's main thread, removing a source of random crashes when adding, removing or toggling creators.
- Busy or failing requests answer with an error message instead of dropping the connection.

### ℹ️ Background Streams
- Measured: a stream in a background tab stops decoding its video by itself (CPU 13.8% → 1.6% of one core) while tapping continues at full speed. No change needed.

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Download the archive or executable for your platform and replace your previous file. Your favorites, settings, cookies and statistics carry over. Coming from v1.2.1 or older? See the v1.2.2 notes: set a cookie passphrase for Cloud Sync and log in to the headless dashboard with the link from the console.

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_123)
