# 🚀 TikTok Live Auto Liker v1.0.7

A major cross-platform release adding official **macOS** and **Linux** support, fixing QR code authentication crashes, resolving live detection & video playback issues, and introducing pixel-perfect UI enhancements.

## ✨ What's New & Improvements

- **Full Cross-Platform Support**:
  - **macOS**: Built natively using Apple's high-performance `WKWebView` with full hardware acceleration, low memory footprint, and Retina display support.
  - **Linux**: Supported via `PyQt6-WebEngine` (Chromium-based) with automatic fallback and headless live monitoring.
  - **Windows**: Continued native support via Microsoft Edge `WebView2`.
- **Fixed QR Code Login Crash**:
  - Corrected login navigation tracking to prevent premature auth triggers while navigating QR code subpages (`passport.tiktok.com`).
  - Added strict Qt slot guards preventing `NoneType` slot crashes and empty tab crashes during authentication transitions.
- **Fixed Live Stream Detection & Avatars**:
  - Fixed an unhandled syntax exception in JavaScript evaluations that caused active streamers to falsely show as offline.
  - Live status and creator profile avatars now update accurately in real-time.
- **Enabled Video Autoplay in Explore & Live Tabs**:
  - Configured WebKit media autoplay permissions and desktop Safari User-Agent so live stream video streams play immediately without freezing.
  - Added lazy-loading and background muting for the Explore tab so no audio can leak when the tab is in the background or during startup.
- **Pixel-Perfect UI Enhancements**:
  - Replaced font-dependent emojis with a custom vector `QPainterPath` heart icon rendered sharply at 20×20 px across all operating systems.
  - Standardized all favorite list action buttons (Tapper, Mute, Delete) to 28×28 px with circular hover effects.
  - Implemented `PulsingTabBar` ensuring mathematical centering of the "System Idle" text and pulsing indicator.

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (Universal `.app` bundle for Apple Silicon & Intel)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update
Simply download the archive or executable for your platform and replace your previous file. All user data, including `favorites.json` and `settings.json`, are 100% compatible and will carry over seamlessly!

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_107)
