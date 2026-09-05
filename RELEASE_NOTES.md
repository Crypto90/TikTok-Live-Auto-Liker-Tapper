# 🚀 TikTok Live Auto Liker v1.1.5

A critical stability and performance release fixing **foreground auto-tapping speed** and the **Explore TikTok blank page issue** on Windows (Edge WebView2), macOS (WebKit), and Linux (QtWebEngine).

---

## 🌟 What's New in v1.1.5

### ⚡ Restored Blazing-Fast Foreground Auto-Tapping
- **Resolved TikTok CSP Worker Blocking**: In v1.1.4, an inline Blob Web Worker was introduced to tick timers across background tabs. However, TikTok's Content Security Policy (CSP) does not permit `blob:` worker origins. When the browser blocked the worker, the tapping loop stalled waiting for worker messages, causing auto-tapping in the active foreground tab to slow down drastically.
- **Native Recursive Tapper Loop**: Removed the CSP-blocked Web Worker and restored clean, jittered in-page recursive `setTimeout` execution with immediate first-tap dispatch. Active tabs tap instantly and smoothly at maximum rate (10–12+ taps/sec).

### 🎯 1-Second Batch Shortfall Catch-Up for Background Tabs
- **Native Burst Engine (`burst_tapper`)**: Instead of running heavy Web Workers or excessive IPC calls, background tabs now utilize an intelligent 1-second shortfall catch-up.
- **Accurate Tap Rates in Background**: When operating systems or browsers clamp background JavaScript timers to ~1 Hz, the Python controller measures the tap count delta each second and dispatches a single burst call (`burst_tapper(needed)`) to fulfill the configured tap rate.
- **Zero Memory/IPC Overhead**: Strictly adheres to architectural guidelines with only 1 IPC call per second, ensuring zero memory leaks and no UI freezes across multiple background live streams.

### 🧭 Fixed Explore TikTok Blank Page & Refresh
- **Reliable Explore Tab Activation**: Fixed an issue where clicking the "Explore TikTok" tab resulted in a blank white page. Removed an overly strict stream guard that blocked navigation when no streamer tabs were currently active.
- **Working Refresh Action**: Clicking the "Refresh" button while viewing the Explore tab now explicitly navigates to `https://www.tiktok.com/` instead of reloading `about:blank`.
- **Protected Stream Closure**: Closing the last active streamer tab now blocks Qt tab signals during widget teardown, ensuring the user is cleanly returned to the "System Idle" screen without unintentionally triggering the Explore tab.

### 🛡️ Cleaned Windows Edge WebView2 Composition
- Removed experimental `--disable-features=CalculateNativeWinOcclusion` flags from process environment variables, which previously interfered with Microsoft Edge WebView2 HWND window composition and caused blank rendering on Windows.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_115)
