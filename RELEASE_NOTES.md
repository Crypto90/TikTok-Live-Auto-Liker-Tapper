# 🚀 TikTok Live Auto Liker v1.1.6

A performance and stability release delivering **macOS live stats & verified like counting fixes**, **elimination of macOS live audio stuttering & buffer bloat**, and **Favorites list tab indicators with clean selection states**.

---

## 🌟 What's New in v1.1.6

### 📊 Fixed macOS Live Stats & Verified Like Counting
- **PyObjC Type Normalization**: On macOS, Apple WebKit (`WKWebView.evaluateJavaScript:completionHandler:`) returns Objective-C collections (`__NSDictionaryM`, `__NSArrayM`, `objc.pyobjc_unicode`) rather than standard Python dictionaries. This caused Python's `isinstance(res, dict)` check in the live stats callback to fail, silently dropping stats on every second.
- **Real-Time Stats Restored**: Live stats now update dynamically on macOS:
  - Verified Likes counter increments with every server acknowledgment.
  - Live Tap Rate (`⚡ X.X/s`) reflects accurate real-time speeds.
  - Active Session Duration (`⏱️ mm:ss`) counts continuously.
  - Verification Rate (`📶 100% Confirmed`) and tab titles (`(❤️ count)`) stay fully in sync.

### 🔊 Eliminated macOS Live Audio Stuttering & Buffer Bloat
- **Automated MediaSource Past-Buffer Eviction**: TikTok Live streams media via HTML5 `MediaSource` (MSE) using separate video and audio `SourceBuffer` tracks. Because TikTok's web player never purges past segments, WebKit's media memory previously grew unbounded over 10–20+ minutes of playback, leading to CoreAudio buffer underruns and severe audio crackling/stuttering.
- **Continuous Sliding Window Cleaner**: Injected an automated media buffer cleaner running every 4 seconds that safely calls `sourceBuffer.remove(0, currentTime - 10)` to purge past audio and video chunks from WebKit's memory. Clamps memory to a constant, lean ~13-second window forever.
- **AudioSession Playback Mode**: Automatically configures `navigator.audioSession.type = 'playback'` to prevent the macOS audio daemon (`audiod`) from throttling or lowering thread priority of WebKit's audio pipeline.
- **Live Clock Drift Correction**: Continuously monitors the live edge buffer gap (`video.buffered.end - video.currentTime`). If playback lags by 2.5–6.0s, it gently catches up at 1.05x speed without audio pitch distortion; if drift exceeds 6s, it immediately jumps to the live edge.

### 🎨 Clean Favorites List Selection & Active Tab Indicators
- **Removed Solid Pink Row Selection**: Removed `selection-background-color: #FE2C55;` and configured `NoSelection` mode with transparent item selection/focus styling. Clicking a favorite no longer leaves an intrusive solid pink highlight that masks the pink "LIVE" text and active heart icon.
- **Sleek Active Tab Left-Border Indicator**: Streamers with currently open tabs are now marked with a clean 3px TikTok-pink left border (`border-left: 3px solid #FE2C55;`) in the Favorites list. When a tab closes or the stream ends, the border cleanly transitions back to transparent.
- **Quick-Switch to Open Streams**: Clicking a favorite whose live stream tab is already open now immediately focuses that streamer's active tab instead of doing nothing.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_116)
