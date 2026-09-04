# 🚀 TikTok Live Auto Liker v1.1.4

A critical performance and reliability release fixing **multi-tab background like throttling** across Windows (Edge WebView2), Linux (QtWebEngine), and macOS (WebKit). All open streamer tabs now tap simultaneously at full configured speed, regardless of which tab is active!

---

## 🌟 What's New in v1.1.4

### ⚡ Unthrottled Multi-Tab Background Auto-Tapping
Fixed an issue where opening multiple live streamer tabs caused background tabs to drastically slow down (dropping to 1–2 likes every few seconds or stalling):
- **Dedicated Inline Web Worker Ticker**: The in-page tapping loop now offloads interval timing to a dedicated background Web Worker thread using message-passing ticks. Unlike standard `setTimeout`/`setInterval`, Web Worker timers run on a separate OS thread and are completely exempt from browser visibility clamping and background tab execution limits.
- **Fallbacks & CSP Immunity**: If Web Workers are restricted by origin or environment policies, the engine automatically falls back to jittered standard timeouts and triggers Python watchdog wakeups.

### 🛡️ Low-Memory & Background Throttling Removal
- **Windows Edge WebView2**: Removed `MemoryUsageTargetLevel = 1` (Low) from background tabs. Previously, this caused WebView2 to aggressively suspend background timers, pause script execution, and throttle background tabs down to 1–2 likes per 10 seconds.
- **Linux QtWebEngine**: Removed `LifecycleState.Passive` on background tabs which instructed Chromium to throttle internal page timers.
- **Engine-Level Anti-Throttling Flags**: Injected Chromium command-line switches (`--disable-background-timer-throttling`, `--disable-backgrounding-occluded-windows`, `--disable-renderer-backgrounding`, `--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,ThrottleDisplayNoneAndVisibilityHiddenCrossOriginIframes`) across both WebView2 and QtWebEngine.

### 🎬 Non-Stalling Media Player Optimization
- Changed background video styling from `visibility: hidden !important` to `opacity: 0.001 !important; pointer-events: none !important;`.
- Eliminates GPU composition load for hidden tabs without triggering Chromium or WebKit's "Media Player Visibility Optimization", which previously paused video decoder loops and stalled media-clock events.

### 👁️ Document Visibility & Focus Spoofing
- Injected property getters spoofing `document.hidden = false`, `document.visibilityState = 'visible'`, and `document.hasFocus = () => true`.
- Convinces TikTok's web player and React components that all background tabs remain actively in focus, preventing client-side sleep timers.

### 🧹 Proportional DOM Hygiene
- DOM element pruning (floating hearts, gift animations, chat message lists) now triggers proportionally every 30 taps in addition to periodic timers, guaranteeing that background tabs keep memory usage minimal without relying on throttled interval timers.

### 🐕 Active Python Watchdog
- The desktop app and headless server now monitor like progression every second and issue immediate wakeup pulses (`wakeup_tapper()`) if any background tab ever falls behind or stalls.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_114)
