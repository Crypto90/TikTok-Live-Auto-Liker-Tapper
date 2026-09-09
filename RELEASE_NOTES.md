# 🚀 TikTok Live Auto Liker v1.1.7

A major feature release introducing **Multi-Stream Grid View**, **Picture-in-Picture (PiP) Floating Players**, **Per-Stream Volume Controls**, **Discord & Telegram Webhook Alerts**, **Native Desktop Notifications**, **Creator Lifetime Profiles**, and **JSON Data Export**.

---

## 🌟 What's New in v1.1.7

### ⊞ Multi-Stream Grid / Matrix View
- **Simultaneous Multi-Stream Monitoring**: Seamlessly toggle between classic Tabbed View and the new **Multi-Stream Grid View** (`⊞ Grid View`) located in the upper-right corner of the tab bar.
- **Dynamic 2 & 3 Column Responsive Grid**: Displays all actively streaming creators side-by-side in responsive cards with independent volume sliders, PiP detach buttons, live like counters, and quick-close buttons.
- **Zero Interruption & Memory Efficient**: Tapping loops continue running in-page without reloading or dropping stream connections when switching between Grid and Tab views.

### ⧉ Picture-in-Picture (PiP) Floating Mini-Player
- **Always-on-Top Floating Video Window**: Pop any active live stream out into an independent floating window (`⧉ PiP`) that stays on top of all other desktop applications while you browse, game, or work.
- **Integrated Controls**: Displays the streamer's name, live like count, and an instant `⤓ Dock` button to return the stream directly to its tab or grid slot.
- **Seamless Tapping Continuity**: Webview detachment retains all active media streams and automated tapping scripts uninterrupted.

### 🔊 Per-Stream Volume Controls & Audio Normalization
- **Individual Volume Sliders (0–100%)**: Adjust volume independently for every streamer with inline sliders in both tab header bars and grid cards.
- **Cross-Engine Audio Control**: Native volume adjustment across Apple WebKit (macOS), Microsoft Edge WebView2 (Windows), and QtWebEngine (Linux).
- **Persistent Volume Preferences**: Individual volume levels are remembered between sessions in settings.

### 🔔 Native Desktop Notifications & Webhooks (Discord & Telegram)
- **Native OS Toast Notifications**: Receive native Notification Center (macOS) and Action Center (Windows/Linux) toasts when a favorite creator starts streaming or crosses like milestones.
- **Discord Webhook Alerts**: Configurable Discord notifications with rich embedded cards, streamer profile avatars, direct stream links, and milestone counters.
- **Telegram Bot Notifications**: Instant push alerts to your Telegram chat or channel whenever creators go live.
- **Configurable Thresholds & Test Connectivity**: Access the new **🔔 Alerts & Webhooks** dialog from the data panel to configure webhook URLs, test message delivery, and toggle notifications.

### 👤 Creator Lifetime Profiles & Detailed History
- **Interactive Avatar Click**: Clicking any creator's avatar in the Favorites list opens their **Creator Profile Dialog**.
- **Lifetime Aggregated KPI Cards**: View total verified likes delivered, total taps dispatched, server delivery rate, total streaming duration, first-seen date, and number of sessions.
- **Complete Session History**: Interactive data table displaying every historical session with date/time, verified likes, tap rate, and session outcome.
- **One-Click Stream Launcher**: Directly jump into an open tab or launch the streamer's live room right from their profile card.

### 📥 JSON & CSV Session Analytics Export
- **One-Click JSON Export**: Beside CSV export, the Analytics dialog now includes **📥 Export JSON**, providing a structured export containing overall KPI aggregates and individual session telemetry for custom reporting or backup.

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

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_117)
