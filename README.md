[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

<img src="icon.png" width="200" height="200" align="center" alt="App Icon">

# TikTok Live Auto Liker / Tapper

A powerful desktop application built with Python, PyQt6, and WebView2 that automatically monitors your favorite TikTok creators and auto-taps (likes) their live streams in real-time.

## 🚀 Features

- **Embedded Browser Engine (QtWebView2)**: Powered by WebView2 for full TikTok web compatibility, background stream rendering, and reliable interaction.
- **Automated Live Stream Monitoring**: Quietly checks your favorite creators in the background using parallel worker threads and automatically opens their stream tabs as soon as they go live.
- **Advanced Real-Time Sorting**: Multi-criteria sorting for your favorites list with direction indicators (▲/▼):
  - **📡 Live Status**: Sorts live creators to the top by default.
  - **🔤 Name**: Alphabetical sorting (A-Z / Z-A).
  - **❤️ Auto-Tapper**: Sort by auto-tapper status (ON / OFF).
  - **🔇 Mute**: Sort by audio state (Unmuted / Muted).
  - Re-sorts instantly when live statuses update, users are added, or settings are toggled.
- **Real-Time Monitoring Stats**: Bottom status bar displaying live statistics (`Monitoring X users │ Y live │ Z liking`) that update immediately upon heart toggles or status checks.
- **Per-User Stream Controls**:
  - **❤️ Heart Toggle**: Enable or disable auto-tapping per creator.
  - **🔊/🔇 Audio Mute Toggle**: Independently control stream audio for each creator.
- **Customizable Liking Rate**:
  - Adjust **Base Delay** (50ms – 500ms) and **Randomization** (0ms – 100ms) to simulate natural tapping speeds.
  - Quick **Reset** button to restore default speed settings.
- **Login & Explore Integration**: Integrated tabs to log into your TikTok account and explore live streams directly inside the application.
- **Modern Dark UI**: Sleek dark-mode interface with styled container boxes, horizontal-scroll prevention, and a pulsing status indicator when idle.

<img width="1372" height="832" alt="image" src="https://github.com/user-attachments/assets/2d662b62-e54f-42ca-a91d-2285641963c6" />


## 📖 How to Use

1. **Launch the Application**: Run the Python application (`python tiktok_live_auto_liker_tapper.py`).
2. **Log In (Optional)**: If prompted, log into your TikTok account via the built-in Login tab.
3. **Add Favorites**: Enter a TikTok username (e.g., `username` or `@username`) under **Favorites** and click **Add**.
4. **Configure Tapping & Audio**:
   - Click the **❤️ (Heart)** icon next to any user to enable/disable auto-tapping for their stream.
   - Click the **🔊/🔇 (Mute)** icon to toggle stream audio on or off.
5. **Sort & Organize**: Use the sort bar above the list (**Name**, **Live**, **Tapper**, **Mute**) to organize your favorites.
6. **Automated Monitoring & Tapping**: Sit back while the app monitors your list in the background. When a favorite user goes live with auto-tapper enabled, their stream opens in a tab and tapping begins automatically!
7. **Adjust Tapping Speed**: Customize base delay and randomization sliders under **Liking Settings** as desired.

## 🔨 Building Standalone Executable (.exe)

You can build a standalone Windows executable (`TikTokLiveAutoLiker.exe`) using PyInstaller:

1. **Install Prerequisites**:
   ```bash
   pip install PyQt6 PyQt6-WebEngine qtwebview2 pyinstaller
   ```

2. **Build executable using PowerShell / CMD**:
   To ensure the WebView2 .NET assemblies (`Microsoft.Web.WebView2.WinForms.dll`, `WebView2Loader.dll`) are correctly bundled, include the `qtwebview2/lib` data path:

   **PowerShell:**
   ```powershell
   $qtlib = (python -c "import qtwebview2, os; print(os.path.join(os.path.dirname(qtwebview2.__file__), 'lib'))")
   pyinstaller --noconsole --onefile --clean --name="TikTokLiveAutoLiker" --add-data "${qtlib};lib" tiktok_live_auto_liker_tapper.py
   ```

3. **Output Executable**:
   The compiled standalone binary will be located in the `dist/` directory (`dist/TikTokLiveAutoLiker.exe`).

## 💖 Support

If you find this project useful, you can support development via Ko-fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_readme)

## ⚖️ Disclaimer

This tool is for educational purposes only. Automated interaction with TikTok may violate their Terms of Service. Use at your own risk.
