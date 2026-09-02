# 🚀 TikTok Live Auto Liker v1.0.9

A hotfix release addressing an audio autoplay regression where switching away from the last live stream would land on the Explore tab and start autoplaying TikTok videos with sound.

## 🐛 Bug Fixes

- **Fixed Explore Tab Autoplay on Stream End**: When the last monitored streamer went offline (or their tab was closed), Qt's internal `removeTab()` would momentarily select the Explore tab before the idle tab redirect could run — causing TikTok videos to load and play audio in the background. Two-layer fix applied:
  - `_on_tab_changed`: Now detects the transient state (no active streams + idle tab is present) and skips loading/unmuting the Explore tab entirely.
  - `_fallback_tab_selection`: Clarified intent of each branch with comments to prevent future regressions.
- **Fixed macOS Gatekeeper Blocking (v1.0.8 hotfix included)**: The macOS app bundle now ships with a proper `CFBundleIdentifier`, a deep ad-hoc codesignature, and an `Open_TikTokLiveAutoLiker.command` launcher script. Double-clicking the launcher on first run strips the quarantine attribute automatically — no more "can't be opened because Apple cannot check it for malicious software" dialog.

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All user data, including `favorites.json` and `settings.json`, are 100% compatible and will carry over seamlessly!

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_109)
