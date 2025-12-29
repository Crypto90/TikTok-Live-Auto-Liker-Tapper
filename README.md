# TikTok Live Auto Liker / Tapper

A lightweight Windows desktop application built with Python and CustomTkinter that automates "liking" on TikTok Live streams. It works by sending virtual keypresses ('L') to a specific TikTok window, even if it is running in the background.

## 🚀 Features
- **Automatic Window Detection:** Automatically finds open browser windows containing "TikTok".
- **Background Support:** Uses Win32 API to send inputs directly to the window without stealing your mouse focus.
- **Modern UI:** Clean, dark-mode interface powered by CustomTkinter.
- **Multi-threaded:** The UI remains responsive while the tapper runs in the background.

## 📖 How to Use
Open TikTok Live in your web browser (Chrome, Edge, etc.).

Launch this application.

Click Refresh List if your window isn't visible.

Select the correct TikTok window from the dropdown.

Click START TAPPING.

To stop, simply click STOP TAPPING.

## ⚠️ Requirements
Windows OS (Required for win32gui and pygetwindow)

Python 3.7+

## ⚖️ Disclaimer
This tool is for educational purposes only. Automated interaction with TikTok may violate their Terms of Service. Use at your own risk.
