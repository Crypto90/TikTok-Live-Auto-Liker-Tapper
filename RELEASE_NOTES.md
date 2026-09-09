# 🚀 TikTok Live Auto Liker v1.1.8

A targeted refinement and stability release introducing **Pure Video Isolation in Picture-in-Picture (PiP)**, a **Continuous Likes Count Badge** when controls auto-hide, and a critical fix for **live stream reloading/hiccups**.

---

## 🌟 What's New in v1.1.8

### 🎬 Pure Video Isolation in Picture-in-Picture (PiP)
- **Zero Website Clutter**: The floating PiP window now strictly isolates the live video player. All surrounding TikTok web chrome—including the left navigation bar, bottom gift drawer ("Rose 1, Rosa 10"), and stream recommendation feeds—are completely suppressed.
- **Hidden Native Player Overlays**: Built-in video controls (`xg-bar`, `xg-controls`, play/pause icons, reload icons, live duration counters) are cleanly hidden inside the player, leaving only the pure live video stream and our custom floating controls.
- **Perfect Aspect Ratio Containment**: Video fills 100% of the floating window with sleek black letterboxing during freeform resizing and aspect ratio switches (📱 9:16 portrait vs 🖥️ 16:9 landscape).
- **Non-Destructive Restoration**: Re-docking the stream back into standard tabs seamlessly restores all original page elements and styles.

### ❤️ Continuous Verified Likes Counter Badge
- **Always Visible**: When the top HUD controls bar automatically fades out after 3.5s of inactivity, a sleek, semi-transparent mini badge (`❤️ {count:,}`) remains visible in the upper-left corner.
- **Real-Time Synchronized**: Counts update dynamically alongside live in-page tapping responses and server verifications.
- **Pass-Through Hover Control**: Moving your mouse anywhere over the window (including over the badge) instantly and smoothly restores the full HUD overlay and playback controls.

### 🛡️ Live Stream Stability & Playback Hiccup Fix
- **Eliminated 30–60s Stream "Hick" / Reload Bug**: Identified and removed background MediaSource buffer pruning and forced playhead seeks (`video.currentTime = liveEdge - 0.8`). Live streams now play continuously without decoder pipeline resets, stalls, or visual reloads.
- **Lightweight AudioSession Keep-Alive**: Retains standard Apple WebKit `navigator.audioSession.type = 'playback'` to prevent background throttling by macOS `audiod` without altering stream buffers.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_118)
