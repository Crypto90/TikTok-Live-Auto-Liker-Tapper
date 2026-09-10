# 🚀 TikTok Live Auto Liker v1.2.1

A precision polish update that **bounds the confirmation rate display to a clean 100.0% maximum** and hardens network batch sniffer accuracy.

---

## 🌟 What's New in v1.2.1

### 📶 Bounded 0.0%–100.0% Confirmed Rate Display
- **Clean Delivery Metric**: Capped the confirmed percentage indicator at `100.0%` max (`min(100.0, ...)`), preventing confusing numbers like `103.5%` or `112%` when TikTok awards combo multipliers or when manual clicks combine with auto-taps.
- **Full Real Likes Preserved**: While the rate display is cleanly capped at 100%, the total verified like counter (`❤️ Verified: X`) remains 100% untouched and continues to credit every single like accepted by TikTok's server.

### 🛡️ Network Sniffer Accuracy Hardening
- **Strict Outgoing Batch Accountability**: Hardened the transparent network hook across both `window.fetch` and `XMLHttpRequest` to strictly use the validated outgoing request `batchCount`.
- **Eliminated Response Overrides**: Removed potential conflicts with ambiguous server-side cumulative fields, ensuring verified likes correspond strictly to accepted like batches.
- **Bounded Closed-Loop Adaptive Ratio**: Ensured the internal adaptive tuner ratio is also clamped to `[0.0, 1.0]`, delivering smooth and stable self-optimizing adjustments.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_121)
