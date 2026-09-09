# 🚀 TikTok Live Auto Liker v1.2.0

A major performance and efficiency release introducing **Smart Adaptive Auto-Throttling**, **clean single-event dispatching**, and **optimized timing defaults** to consistently deliver **90%+ server confirmation rates** for likes.

---

## 🌟 What's New in v1.2.0

### 🧠 Smart Adaptive Auto-Throttling (Closed-Loop Rate Optimizer)
- **Automatic Confirmation Maximization**: The in-page tapper now features a closed-loop rate controller that continuously monitors verified server responses versus dispatched taps.
- **Dynamic Throttle Backoff**: If TikTok's server or client debounce begins dropping taps (confirmation rate falls below 78%), the engine smoothly backs off base delay by `+15ms` (up to 260ms max) until confirmation recovers.
- **Intelligent Speed Probing**: When confirmation rate is stellar (>=90%), the engine gently probes faster by `-5ms` (down to 130ms min), continuously seeking the highest like rate TikTok will accept without dropping.
- **Dynamic Live Feedback**: The confirmation badge in the stream stats bar now displays live adaptive latency in real time (e.g., `📶 94.2% Confirmed (165ms)`).
- **Toggleable via UI & Web Dashboard**: A new *"Adaptive Rate (Auto-Maximize Confirmed %)"* checkbox is available in the desktop settings panel, web remote interface, and headless runner.

### 🎯 Clean Single-Event Dispatching
- **Eliminated Event Collisions**: Previously, both the `'L'` key and a synthetic `dblclick` were fired in the exact same millisecond. Because TikTok listens to both, the second event triggered immediate debounce drops.
- **Native Hotkey Emulation**: Dispatches pure, bubbling `'L'` keyboard events directly matching TikTok's native desktop keyboard shortcut architecture.
- **Chat Input Safeguard**: Prevents keyboard event leaks if the user interacts with chat text fields or search boxes.

### ⚡ Optimal Sweet-Spot Timing Defaults (165ms / 35ms)
- **Debounce-Aligned Defaults**: Updated baseline defaults from legacy 100ms / 50ms to the proven sweet spot: **165ms Base Delay + 35ms Randomization Jitter** (~182ms average interval).
- **Debounce-Respecting Background Bursts**: Catch-up bursts in minimized or background tabs now space taps by `Math.max(160, baseDelay)` ms instead of firing tight synchronous bursts that violate TikTok's debounce window.
- **Automatic Setting Migration**: Existing users with previous 100ms/50ms defaults are seamlessly migrated to 165ms/35ms upon launch while preserving all custom configurations.

### 🔍 Enhanced Network Hook & Response Verification
- **Multi-Format Request Body Parsing**: Transparent network sniffer now decodes `URLSearchParams`, `FormData`, and JSON body payloads to accurately track batch like counts.
- **Precise Server Count Extraction**: Extracts exact accepted like counts (`data.data.count`) from TikTok webcast responses for 100% verified accounting.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_120)
