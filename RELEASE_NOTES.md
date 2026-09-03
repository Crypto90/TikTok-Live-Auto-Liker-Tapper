# 🚀 TikTok Live Auto Liker v1.1.0

A critical stability and cross-platform compatibility release resolving false offline detections on Windows, eliminating the stuck "Checking..." UI status on first check run, and hardening live detection across all platforms.

## 🐛 Bug Fixes & Improvements

- **Fixed False Offline Detection on Windows**: Microsoft Edge WebView2 (`qtwebview2`) wraps JavaScript evaluations in an async arrow function block body `(async () => { {script} })()`, which evaluated to `undefined` without a top-level `return` statement. `WindowsWebView2Widget.evaluate_js` now automatically wraps expressions in `return ({clean_js});`, properly passing detection dictionaries, avatar URLs, and stream health metrics to the app on Windows.
- **Fixed Stuck "Checking..." Status on First Run**: Previously, `consecutive_offline >= 2` flap protection was applied indiscriminately to all users, causing non-live favorites to stay stuck displaying `"Checking..."` for the entire first 60 seconds until the second run triggered. This flap protection is now scoped strictly to creators who were actively streaming or known live; non-live creators immediately update to `"Offline"` on the first check.
- **Error Guarding for UI Status**: Network or timeout check failures (`is_error=True`) now properly transition new or non-live favorites away from `"Checking..."` so the list remains clean and accurate.
- **Hardened Live Stream & Avatar Detection**:
  - `CheckerWorker._check_js` now verifies that the active URL is on `/live`, uses a multi-selector query for creator avatars (`img[data-e2e="user-avatar"], img[class*="Avatar"], img[class*="avatar"]`), and checks language-independent end overlay elements (`[data-e2e="live-end-card"], [data-e2e="live-end-follow"]`) plus multilingual end text indicators.
  - Redirect checks in `_on_nav_completed` are now case-insensitive.
  - Multilingual ended-stream indicators were also added to `LiveTab._check_stream_health_js`.

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All user data, including `favorites.json` and `settings.json`, are 100% compatible and will carry over seamlessly!

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_110)
