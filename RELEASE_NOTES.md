# 🚀 TikTok Live Auto Liker v1.0.8

A hotfix release addressing an issue where the app could get stuck on a blank page instead of displaying the "System Idle" tab after logging in.

## 🐛 Bug Fixes

- **Fixed Tab Display After Login**: Corrected the tab cleanup and reordering sequence so the login tab is removed before evaluating the waiting tab state. This ensures the "System Idle" tab is immediately displayed and active upon authentication instead of leaving the user on an uninitialized Explore tab.
- **Improved Tab State Resilience**: Ensures `_fallback_tab_selection` always targets the active waiting tab or live stream tab after authentication state transitions.

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (Universal `.app` bundle for Apple Silicon & Intel)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update
Simply download the archive or executable for your platform and replace your previous file. All user data, including `favorites.json` and `settings.json`, are 100% compatible and will carry over seamlessly!

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_108)
