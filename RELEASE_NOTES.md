# 🚀 TikTok Live Auto Liker v1.1.2

An essential feature update bringing **Web-Based Cloud Sync Configuration**, **Cross-Device TikTok Session & Cookie Synchronization**, and **In-Browser Session Management** to the Headless Linux Server.

---

## 🌟 What's New in v1.1.2

### ☁️ Web Dashboard Cloud Sync Configuration
You can now configure, test, and activate multi-device cloud synchronization directly from your browser on `http://server-ip:8080`:
- **Provider Selector**: Switch seamlessly between **Shared Folder / Cloud Drive** (Google Drive, Dropbox, OneDrive, Syncthing), **WebDAV** (Nextcloud, ownCloud, Fastmail), and **REST API / Central Sync Server**.
- **Live Connection Diagnostics**: Dedicated **`🧪 Test Connection`** button validates sync credentials, directory write permissions, and remote server reachability with instant feedback.
- **Save & Sync Now**: Apply configurations and execute an immediate two-way synchronization in a single click without restarting or accessing the server terminal.

### 🍪 Cross-Device TikTok Session & Cookie Synchronization
- **Authenticated Headless Operation**: Synchronizes your TikTok login session cookies (`sessionid`, etc.) across all your Macs, Windows PCs, and headless Linux servers.
- **Likes Count to Your Account**: Ensures that all streams monitored and tapped by your 24/7 Linux server or background devices count directly under your personal TikTok profile.
- **Privacy & Security First**: Fully opt-in toggle (`Sync TikTok login session & cookies`) with conflict-free Last-Write-Wins (LWW) resolution and automatic session invalidation upon sign out.

### 🌐 In-Browser Cookie & Authentication Management
- **Real-Time Session Status**: View current authentication state (`Authenticated` / `No Session Found`), active cookie count, and last synchronization timestamp in the Web Dashboard.
- **Direct Cookie Import**: Seamlessly import session cookies into headless servers via raw `sessionid` tokens, JSON arrays, key-value objects, or HTTP `Cookie:` request headers with automatic format normalization.
- **One-Click Session Clearing**: Clear active cookies anytime directly from the Web Dashboard.

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All existing configurations (`favorites.json`, `settings.json`, `cookies.json`) are 100% compatible and will carry over seamlessly!

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_112)

