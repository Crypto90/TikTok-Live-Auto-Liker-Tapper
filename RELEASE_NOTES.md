# 🚀 TikTok Live Auto Liker v1.1.1

A major feature release introducing seamless **Multi-Device Synchronization**, a dedicated **Headless Linux Server Mode**, and a built-in modern dark-themed **Web Dashboard**.

---

## 🌟 What's New in v1.1.1

### ☁️ Multi-Device Synchronization
Keep all your favorites, auto-tapper toggles (❤️), audio states (🔇), and liking speeds in sync across your **Mac**, **Windows gaming PC**, **secondary Windows laptops**, and **Linux servers**:
- **3 Native Sync Backends**:
  - **📁 Shared Folder / Cloud Drive**: Point to any folder inside your **Dropbox**, **OneDrive**, **Google Drive**, or **Syncthing** directory. Zero setup or third-party accounts required!
  - **🌐 WebDAV Remote**: Direct HTTPS sync with **Nextcloud**, **ownCloud**, or **Fastmail**.
  - **⚡ REST API / Central Sync Server**: Self-hosted sync server using the included zero-dependency `sync_server.py`.
- **Conflict-Free Merging (LWW + Tombstones)**: State-based CRDT merging with deletion tombstones ensures that creators removed on one computer stay deleted across all connected devices.
- **Auto-Sync & Debouncing**: Automatic background sync every 60 seconds and debounced auto-push (2 seconds) whenever you add/remove creators, toggle hearts, or move speed sliders.
- **In-App Cloud Sync Panel**: Click the new **`☁️ Cloud Sync`** button in the sidebar under Data Management to configure sync, test connections, and sync on demand.

### 🖥️ Headless Linux Server Mode
Run the Auto-Liker 24/7 on an unmonitored home server, Raspberry Pi, or cloud VPS:
- Mounts live streams in the background, injects native auto-tappers, mutes audio, and monitors stream health.
- Automatic virtual display detection (`Xvfb`) for headless Linux servers without X11 or Wayland.
- Launch directly via:
  ```bash
  xvfb-run -a python headless_runner.py --port 8080
  # Or via main app CLI:
  xvfb-run -a python tiktok_live_auto_liker_tapper.py --headless --port 8080
  ```

### ⚡ Responsive Web Dashboard (`http://server-ip:8080`)
A built-in single-page web interface served directly by the headless runner (zero Node.js or npm dependencies):
- **Live Streams Cards**: Real-time cards of currently streaming creators with live pulsing badges, tap speeds, and quick ❤️/🔇 toggles.
- **Favorites Manager**: Add or remove creators, toggle auto-tapping and audio, and search creators in real-time.
- **Speed Controls**: Adjust Base Delay and Randomization sliders remotely with live numerical feedback.
- **Sync Now**: Trigger instant multi-device sync with one click.
- **Activity Logs**: Real-time console log viewer.

### 📦 Server Deployment Assets
- **Systemd Service**: Preconfigured `server/tiktok-autoliker.service` unit file for 24/7 background operation.
- **Docker & Compose**: Preconfigured `server/Dockerfile` and `server/docker-compose.yml` (`docker compose up -d`).

---

## 📦 Downloads

Download the standalone package for your operating system below:

- **Windows**: `TikTokLiveAutoLiker.exe` (Standalone executable)
- **macOS**: `TikTokLiveAutoLiker-macOS.zip` (App bundle + `Open_TikTokLiveAutoLiker.command` launcher — **use the launcher on first run to bypass Gatekeeper**)
- **Linux**: `TikTokLiveAutoLiker-Linux.tar.gz` (Standalone binary for 64-bit Linux)

## 📥 How to update

Simply download the archive or executable for your platform and replace your previous file. All user data, including `favorites.json` and `settings.json`, are 100% compatible and will carry over seamlessly!

---

## 💖 Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_release_111)
