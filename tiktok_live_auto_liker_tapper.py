import os
import sys

# Completely suppress C++ stderr console spam from QtWebEngine & QFont
# sys.stderr = open(os.devnull, 'w')
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --log-level=3"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"

import json
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QSpinBox, QSlider,
    QTabWidget, QSplitter, QGroupBox, QFormLayout, QMessageBox, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject, pyqtSlot, QMetaObject, qInstallMessageHandler
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap, QPainterPath, QDesktopServices, QFont
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qtwebview2.widget import QtWebView2Widget
import math
import time

def _qt_message_handler(mode, context, message):
    if "setPointSize" in message or "Point size" in message:
        return

APP_VERSION = "v1.0.2"
GITHUB_REPO = "Crypto90/TikTok-Live-Auto-Liker-Tapper"

FAVORITES_FILE = "favorites.json"
SETTINGS_FILE = "settings.json"

WAITING_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        margin: 0;
        padding: 0;
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        overflow: hidden;
        user-select: none;
    }
    .pulse-container {
        position: relative;
        width: 150px;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px;
    }
    .core {
        width: 50px;
        height: 50px;
        background-color: #FE2C55;
        border-radius: 50%;
        z-index: 10;
        box-shadow: 0 0 20px rgba(254, 44, 85, 0.6);
    }
    .ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border: 2px solid #25F4EE;
        border-radius: 50%;
        animation: pulse 4.5s infinite cubic-bezier(0.215, 0.61, 0.355, 1);
        opacity: 0;
    }
    .ring:nth-child(1) { animation-delay: 0s; }
    .ring:nth-child(2) { animation-delay: 1.5s; }
    .ring:nth-child(3) { animation-delay: 3.0s; }
    @keyframes pulse {
        0% { transform: scale(0.3); opacity: 0.8; }
        100% { transform: scale(1.5); opacity: 0; }
    }
    h2 {
        font-size: 26px;
        margin: 10px 0;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    p {
        color: #888;
        font-size: 15px;
        max-width: 450px;
        text-align: center;
        line-height: 1.6;
    }
</style>
</head>
<body>
    <div class="pulse-container">
        <div class="ring"></div>
        <div class="ring"></div>
        <div class="ring"></div>
        <div class="core"></div>
    </div>
    <h2>Monitoring Favorites...</h2>
    <p>The Auto-Liker is quietly checking your favorite creators in the background.<br><br>Ensure the <span style="color: #FE2C55; font-weight: bold;">❤️ Heart</span> toggle is turned on for creators you wish to auto-tap. Whenever an enabled creator goes live, their stream tab will open automatically and tapping will start!</p>
</body>
</html>
"""


class UserListItem(QWidget):
    def __init__(self, username, is_enabled=True, is_muted=True):
        super().__init__()
        self.username = username
        self.has_avatar = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(32, 32)
        self.avatar_label.setStyleSheet("background-color: #333; border-radius: 16px;")
        
        self.name_label = QLabel(username)
        self.name_label.setStyleSheet("font-weight: bold; color: #E0E0E0; font-size: 9.5pt;")
        
        self.status_label = QLabel("Checking...")
        self.status_label.setStyleSheet("color: #888; font-size: 8.5pt;")
        
        # Heart Toggle Button
        from PyQt6.QtWidgets import QToolButton
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("❤")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_tapper_enabled(is_enabled)
        
        self.mute_btn = QToolButton()
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_muted(is_muted)
        
        self.del_btn = QToolButton()
        self.del_btn.setText("❌")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("color: #888; background: transparent; border: none; font-size: 10pt;")
        
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.mute_btn)
        layout.addWidget(self.del_btn)
        
    def set_tapper_enabled(self, is_enabled):
        if is_enabled:
            self.toggle_btn.setStyleSheet("color: #FE2C55; background: transparent; border: none; font-size: 12pt;")
            self.toggle_btn.setToolTip("Auto-Tapper: ON")
        else:
            self.toggle_btn.setStyleSheet("color: #555; background: transparent; border: none; font-size: 12pt;")
            self.toggle_btn.setToolTip("Auto-Tapper: OFF")
        
    def set_muted(self, muted):
        if muted:
            self.mute_btn.setText("🔇")
            self.mute_btn.setStyleSheet("color: #888; background: transparent; border: none; font-size: 12pt;")
            self.mute_btn.setToolTip("Muted")
        else:
            self.mute_btn.setText("🔊")
            self.mute_btn.setStyleSheet("color: #4CAF50; background: transparent; border: none; font-size: 12pt;")
            self.mute_btn.setToolTip("Unmuted")

    def set_status(self, is_live):
        if is_live:
            self.status_label.setText("LIVE")
            self.status_label.setStyleSheet("color: #FE2C55; font-weight: bold; font-size: 8.5pt;")
        else:
            self.status_label.setText("Offline")
            self.status_label.setStyleSheet("color: #888; font-size: 8.5pt;")

    def set_avatar(self, pixmap):
        target = QPixmap(32, 32)
        target.fill(Qt.GlobalColor.transparent)
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addEllipse(0, 0, 32, 32)
        painter.setClipPath(path)
        
        scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        x = (32 - scaled_pixmap.width()) // 2
        y = (32 - scaled_pixmap.height()) // 2
        
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        self.avatar_label.setStyleSheet("")
        self.avatar_label.setPixmap(target)

class SettingsManager:
    @staticmethod
    def load_favorites():
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {user: True for user in data}
                    return data
            except:
                pass
        return {}

    @staticmethod
    def save_favorites(favorites):
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(favorites, f)

    @staticmethod
    def load_settings():
        default_settings = {
            "like_delay_ms": 100,
            "randomization_ms": 50
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    default_settings.update(settings)
            except:
                pass
        return default_settings

    @staticmethod
    def save_settings(settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)


class CheckerWorker(QObject):
    status_checked = pyqtSignal(str, bool, str, bool)  # (username, is_live, avatar_url, is_error)
    ready = pyqtSignal(object)

    # Timeout: if a check doesn't complete in 20s, force it done (reported as error for retry)
    TIMEOUT_MS = 20000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.webview = QtWebView2Widget(
            lazyload=False,
            user_data_folder="./userdata",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        )
        self.webview._init_settings_hook = self._on_core_init
        self.current_user = None
        self._nav_handler = None
        self._done = False

        self._watchdog = QTimer(self)
        self._watchdog.setSingleShot(True)
        self._watchdog.timeout.connect(self._on_timeout)

    def check_user(self, username):
        self.current_user = username
        self._done = False
        self._watchdog.start(self.TIMEOUT_MS)
        self.webview.load_url(f"https://www.tiktok.com/@{username}/live")

    def _finish(self, is_live, avatar_url="", is_error=False):
        """Single exit point — prevents double-emitting if watchdog fires late."""
        if self._done:
            return
        self._done = True
        self._watchdog.stop()
        self.status_checked.emit(self.current_user, bool(is_live), str(avatar_url), bool(is_error))
        self.ready.emit(self)

    @pyqtSlot()
    def _on_timeout(self):
        """Watchdog fired — worker is stuck, report as error for retry."""
        self._finish(False, "", is_error=True)

    def _on_core_init(self, core_wv2):
        try:
            core_wv2.IsMuted = True
        except Exception:
            pass

        def on_nav_completed(sender, args):
            if not args.IsSuccess:
                QMetaObject.invokeMethod(self, "_nav_failed", Qt.ConnectionType.QueuedConnection)
                return
            
            current_url = str(sender.Source)
            # If TikTok redirected away from /live to profile, creator is confirmed OFFLINE
            if "/live" not in current_url:
                QMetaObject.invokeMethod(self, "_nav_offline", Qt.ConnectionType.QueuedConnection)
                return
                
            QTimer.singleShot(4000, lambda: QMetaObject.invokeMethod(self, "_check_js", Qt.ConnectionType.QueuedConnection))
            
        self._nav_handler = on_nav_completed
        core_wv2.NavigationCompleted += self._nav_handler

    @pyqtSlot()
    def _nav_failed(self):
        """Navigation error / network failure."""
        self._finish(False, "", is_error=True)

    @pyqtSlot()
    def _nav_offline(self):
        """Redirected away from /live — clean offline result."""
        self._finish(False, "", is_error=False)

    @pyqtSlot()
    def _check_js(self):
        if self._done:
            return
        js_code = """return (function() {
            var video = document.querySelector('video') !== null || 
                        document.querySelector('[data-e2e="live-video"]') !== null ||
                        document.querySelector('.tiktok-web-player') !== null;
            var img = document.querySelector('img[class*="Avatar"], img[class*="avatar"]');
            var avatar = img ? img.src : '';
            return JSON.stringify({ is_live: video, avatar_url: avatar });
        })();"""
        self.webview.evaluate_js(js_code, self._on_js_result)

    def _on_js_result(self, result_dict):
        res_str = result_dict.get('result', '{}')
        if not isinstance(res_str, str): res_str = '{}'
        try:
            import json
            data = json.loads(res_str)
            is_live = data.get('is_live', False)
            avatar_url = data.get('avatar_url', '')
            self._finish(is_live, avatar_url, is_error=False)
        except Exception:
            self._finish(False, "", is_error=True)


class LiveChecker(QObject):
    status_checked = pyqtSignal(str, bool, str, bool)

    def __init__(self, pool_size=4, max_retries=2):
        super().__init__()
        self.queue = []
        self.retry_counts = {}
        self.max_retries = max_retries
        self.workers = []
        self.idle_workers = []
        for _ in range(pool_size):
            worker = CheckerWorker(self)
            worker.status_checked.connect(self._on_worker_status)
            worker.ready.connect(self._on_worker_ready)
            self.workers.append(worker)
            self.idle_workers.append(worker)

    def check_users(self, users):
        if not users: return
        for u in users:
            self.retry_counts[u] = 0
            if u not in self.queue:
                self.queue.append(u)
        self._process_queue()

    def _on_worker_status(self, username, is_live, avatar_url, is_error):
        if is_error and self.retry_counts.get(username, 0) < self.max_retries:
            self.retry_counts[username] += 1
            # Schedule retry after a 2-second pause without emitting error to main app
            QTimer.singleShot(2000, lambda u=username: self._requeue_user(u))
        else:
            self.status_checked.emit(username, is_live, avatar_url, is_error)

    def _requeue_user(self, username):
        if username not in self.queue:
            self.queue.append(username)
        self._process_queue()

    def _on_worker_ready(self, worker):
        self.idle_workers.append(worker)
        self._process_queue()

    def _process_queue(self):
        while self.queue and self.idle_workers:
            user = self.queue.pop(0)
            worker = self.idle_workers.pop(0)
            worker.check_user(user)

    def cleanup(self):
        for worker in self.workers:
            if getattr(worker, 'webview', None):
                worker.webview.close()
                worker.webview.deleteLater()

class LiveTab(QWidget):
    def __init__(self, username, settings, tapper_enabled=True, is_muted=True):
        super().__init__()
        self.username = username
        self.settings = settings
        self.tapper_enabled = tapper_enabled
        self.is_muted = is_muted
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.webview = QtWebView2Widget(
            url=f"https://www.tiktok.com/@{self.username}/live",
            lazyload=False,
            user_data_folder="./userdata",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        )
        layout.addWidget(self.webview)

        self.like_timer = QTimer(self)
        self.like_timer.timeout.connect(self._do_like)
        self.like_timer.start(self._get_next_delay())
        
        self.mute_timer = QTimer(self)
        self.mute_timer.timeout.connect(self._enforce_mute)
        self.mute_timer.start(500)

    def _enforce_mute(self):
        js = f"document.querySelectorAll('video, audio').forEach(v => v.muted = {'true' if self.is_muted else 'false'});"
        self.webview.evaluate_js(js)
        
    def set_muted(self, muted):
        self.is_muted = muted
        self._enforce_mute()

    def _get_next_delay(self):
        base = self.settings.get("like_delay_ms", 100)
        import random
        rand = self.settings.get("randomization_ms", 50)
        return max(50, base + random.randint(0, rand))

    def _do_like(self):
        if not getattr(self, 'tapper_enabled', True):
            self.like_timer.start(self._get_next_delay())
            return
            
        delay = self._get_next_delay()
        burst_js = "setTimeout(triggerTap, 50);" if delay > 400 else ""
        
        js_code = f"""
        (function() {{
            // Spoof visibility so TikTok thinks the background tab is active
            if (document.visibilityState !== 'visible') {{
                Object.defineProperty(document, 'visibilityState', {{value: 'visible', writable: false}});
                Object.defineProperty(document, 'hidden', {{value: false, writable: false}});
            }}
            
            function triggerTap() {{
                // Dispatch 'L' key with proper bubbling
                var keydown = new KeyboardEvent('keydown', {{key: 'l', code: 'KeyL', keyCode: 76, which: 76, bubbles: true, cancelable: true}});
                var keyup = new KeyboardEvent('keyup', {{key: 'l', code: 'KeyL', keyCode: 76, which: 76, bubbles: true, cancelable: true}});
                document.dispatchEvent(keydown);
                document.dispatchEvent(keyup);
                
                // Also try double-clicking the video container as a fallback
                var likeArea = document.querySelector('[data-e2e="live-video"]') || document.querySelector('.tiktok-web-player');
                if (likeArea) {{
                    var clickEvent = new MouseEvent('dblclick', {{
                        view: window,
                        bubbles: true,
                        cancelable: true
                    }});
                    likeArea.dispatchEvent(clickEvent);
                }}
            }}
            
            triggerTap();
            {burst_js}
        }})();
        """
        self.webview.evaluate_js(js_code)
        self.like_timer.start(delay)
        
    def cleanup(self):
        self.like_timer.stop()
        if hasattr(self, 'mute_timer'):
            self.mute_timer.stop()
        self.webview.load_url("about:blank")
        self.webview.deleteLater()
        
    def update_settings(self, settings):
        self.settings = settings

class PulsingDot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 14) # Match height of 14px text
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)
        self.start_time = time.time()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        elapsed = time.time() - self.start_time
        opacity = 0.3 + 0.7 * ((math.sin(elapsed * 4.0) + 1) / 2)
        
        color = QColor("#FE2C55")
        color.setAlphaF(opacity)
        
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Nudge dot down to visually align with text baseline
        painter.drawEllipse(1, 4, 8, 8)
        painter.end()


class TikTokAutoLikerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"TikTok Live Auto Liker {APP_VERSION}")
        self.resize(1370, 800)

        self.favorites = SettingsManager.load_favorites()
        self.settings = SettingsManager.load_settings()
        self.active_streams = {} 
        self.fav_widgets = {}
        self.sort_key = 'live'
        self.sort_reverse = True   # Live-first by default
        self.sort_buttons = {}
        self.avatar_manager = QNetworkAccessManager(self)
        os.makedirs("avatars", exist_ok=True)
        
        self.is_monitoring = False
        self.is_logged_in = False
        self.login_webview = None
        self.waiting_webview = None
        self.explore_webview = None
        self._has_handled_login = False
        
        self.floating_dot = None
        self.dot_pos_timer = QTimer(self)
        self.dot_pos_timer.timeout.connect(self._update_floating_dot)
        self.dot_pos_timer.start(30)
        
        self.dot_pos_timer.start(30)
        
        self._apply_stylesheet()
        self._setup_ui()
        self._setup_webview_engine()
        QTimer.singleShot(3000, self.check_for_updates)

    def _open_kofi(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_app"))

    def _add_user_list_item(self, username):
        item = QListWidgetItem(self.fav_list)
        item.setData(Qt.ItemDataRole.UserRole, username)
        
        is_enabled = self.favorites.get(username, True)
        is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
        widget = UserListItem(username, is_enabled, is_muted)
        widget.toggle_btn.clicked.connect(lambda: self.toggle_tapper(username))
        widget.mute_btn.clicked.connect(lambda: self.toggle_mute(username))
        widget.del_btn.clicked.connect(lambda: self.remove_favorite(username))
        
        avatar_path = os.path.join("avatars", f"{username}.png")
        if os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
            widget.set_avatar(pixmap)
        
        item.setSizeHint(widget.sizeHint())
        self.fav_list.setItemWidget(item, widget)
        self.fav_widgets[username] = widget
        
    def _on_user_clicked(self, item):
        username = item.data(Qt.ItemDataRole.UserRole)
        if username not in self.active_streams:
            self.status_label.setText(f"● Opening stream manually: @{username}")
            tapper_enabled = self.favorites.get(username, True)
            is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
            tab = LiveTab(username, self.settings, tapper_enabled, is_muted)
            
            prefix = "❤️ " if tapper_enabled else ""
            idx = self.tabs.addTab(tab, f"{prefix}LIVE: @{username}")
            self.tabs.setCurrentIndex(idx)
            
            self.active_streams[username] = tab
            self._update_waiting_tab()

    def toggle_mute(self, username):
        if username in self.favorites:
            muted_users = self.settings.setdefault("muted_users", {})
            current = muted_users.get(username, True)
            muted_users[username] = not current
            self.fav_widgets[username].set_muted(not current)
            self.save_settings_ui()
            
            if username in self.active_streams:
                self.active_streams[username].set_muted(not current)
            self._sort_list()

    def toggle_tapper(self, username):
        if username in self.favorites:
            current = self.favorites[username]
            new_state = not current
            self.favorites[username] = new_state
            self.fav_widgets[username].set_tapper_enabled(new_state)
            SettingsManager.save_favorites(self.favorites)

            if username in self.active_streams:
                # Tab already open — just update its tapper state and label
                self.active_streams[username].tapper_enabled = new_state
                tab_idx = self.tabs.indexOf(self.active_streams[username])
                if tab_idx != -1:
                    prefix = "❤️ " if new_state else ""
                    self.tabs.setTabText(tab_idx, f"{prefix}LIVE: @{username}")
            elif new_state and username in getattr(self, 'known_live', set()):
                # Heart turned ON and user is already confirmed live — open tab immediately
                is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
                tab = LiveTab(username, self.settings, tapper_enabled=True, is_muted=is_muted)
                idx = self.tabs.addTab(tab, f"❤️ LIVE: @{username}")
                self.tabs.setCurrentIndex(idx)
                self.active_streams[username] = tab
                self._update_waiting_tab()

            # Immediately refresh the monitoring stats bar if not mid-scan
            if getattr(self, '_pending_checks', 0) == 0:
                self._update_status_label()
            self._sort_list()

    def _download_avatar(self, username, url):
        if not url: return
        req = QNetworkRequest(QUrl(url))
        req.setAttribute(QNetworkRequest.Attribute.User, username)
        reply = self.avatar_manager.get(req)
        reply.finished.connect(lambda r=reply: self._on_avatar_downloaded(r))
        
    def _on_avatar_downloaded(self, reply):
        username = reply.request().attribute(QNetworkRequest.Attribute.User)
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                pixmap.save(os.path.join("avatars", f"{username}.png"))
                if username in self.fav_widgets:
                    self.fav_widgets[username].set_avatar(pixmap)
        reply.deleteLater()

    def _get_zero_widget(self):
        w = QWidget()
        w.setFixedSize(0, 0)
        return w

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#left_panel {
                background-color: #121212;
            }
            QWidget {
                color: #E0E0E0;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QSplitter::handle {
                background: #2a2a2a;
            }
            QGroupBox {
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #FE2C55;
                font-weight: bold;
                font-size: 15px;
            }
            QLineEdit, QSpinBox, QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #FE2C55;
            }
            QLineEdit:focus, QSpinBox:focus, QListWidget:focus {
                border: 1px solid #25F4EE;
            }
            QPushButton {
                background-color: #FE2C55;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0284D;
            }
            QPushButton:pressed {
                background-color: #C12242;
            }
            QPushButton#remove_btn {
                background-color: #333;
                color: #FF5A5A;
            }
            QPushButton#remove_btn:hover {
                background-color: #444;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #121212;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #888;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a2a2a;
                color: #fff;
                border-bottom: 2px solid #25F4EE;
            }
            QLabel#status_label {
                color: #888;
                font-size: 12px;
            }
        """)

    def closeEvent(self, event):
        try:
            if getattr(self, 'checker', None):
                self.checker.cleanup()
            
            if getattr(self, 'explore_webview', None):
                self.explore_webview.close()
            if getattr(self, 'waiting_webview', None):
                self.waiting_webview.close()
                
            for tab in self.active_streams.values():
                tab.webview.close()
        except Exception:
            pass
        event.accept()

    def _setup_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15)
        left_panel.setMaximumWidth(380)

        title_header = QHBoxLayout()
        title_lbl = QLabel("Live Auto Liker")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #fff;")
        
        coffee_btn = QPushButton("☕ Buy me a coffee")
        coffee_btn.setToolTip("Support development on Ko-fi")
        coffee_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        coffee_btn.setStyleSheet("""
            QPushButton {
                background-color: #262015;
                color: #FFC107;
                border: 1px solid #3d3118;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #332b1c;
                border-color: #544321;
                color: #FFD54F;
            }
            QPushButton:pressed {
                background-color: #1f1a11;
            }
        """)
        coffee_btn.clicked.connect(self._open_kofi)
        
        title_header.addWidget(title_lbl)
        title_header.addStretch()
        title_header.addWidget(coffee_btn)
        left_layout.addLayout(title_header)

        # Favorites container: title row above a styled border box
        fav_container = QWidget()
        fav_container_layout = QVBoxLayout(fav_container)
        fav_container_layout.setContentsMargins(0, 0, 0, 0)
        fav_container_layout.setSpacing(5)

        # Header row: "Favorites" title
        fav_header = QHBoxLayout()
        fav_header.setContentsMargins(12, 0, 4, 0)
        fav_title_lbl = QLabel("Favorites")
        fav_title_lbl.setStyleSheet(
            "color: #FE2C55; font-weight: bold; font-size: 15px; background: transparent; border: none;"
        )
        fav_header.addWidget(fav_title_lbl)
        fav_header.addStretch()
        fav_container_layout.addLayout(fav_header)

        # Bordered box (same look as Liking Settings)
        fav_box = QFrame()
        fav_box.setObjectName("fav_box")
        fav_box.setStyleSheet(
            "QFrame#fav_box { border: 1px solid #333; border-radius: 8px; background-color: #1a1a1a; }"
        )
        fav_layout = QVBoxLayout(fav_box)
        fav_layout.setSpacing(10)
        fav_layout.setContentsMargins(10, 12, 10, 10)

        add_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Username")
        add_btn = QPushButton("Add")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_favorite)
        add_layout.addWidget(self.search_input)
        add_layout.addWidget(add_btn)
        fav_layout.addLayout(add_layout)

        # --- Sort bar ---
        sort_bar = QHBoxLayout()
        sort_bar.setSpacing(4)
        sort_lbl = QLabel("Sort:")
        sort_lbl.setStyleSheet("color: #555; font-size: 11px; padding: 0;")
        sort_bar.addWidget(sort_lbl)
        sort_defs = [
            ('name',   'Name'),
            ('live',   '\U0001f4e1 Live'),
            ('tapper', '\u2764 Tapper'),
            ('mute',   '\U0001f507 Mute'),
        ]
        for s_key, s_label in sort_defs:
            btn = QPushButton(s_label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=s_key: self._on_sort_clicked(k))
            btn.setFixedHeight(24)
            self.sort_buttons[s_key] = btn
            sort_bar.addWidget(btn)
        fav_layout.addLayout(sort_bar)

        self.fav_list = QListWidget()
        self.fav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fav_list.itemClicked.connect(self._on_user_clicked)
        for fav in self.favorites:
            self._add_user_list_item(fav)
        self._sort_list()          # Sort once after all users are added
        self._update_sort_buttons()
        fav_layout.addWidget(self.fav_list)

        fav_container_layout.addWidget(fav_box)
        left_layout.addWidget(fav_container, 1)

        # Settings container: title+Reset row above a styled border box
        settings_container = QWidget()
        settings_container_layout = QVBoxLayout(settings_container)
        settings_container_layout.setContentsMargins(0, 0, 0, 0)
        settings_container_layout.setSpacing(5)

        # Header row: "Liking Settings" title left, Reset button right
        settings_header = QHBoxLayout()
        settings_header.setContentsMargins(12, 0, 4, 0)
        settings_title_lbl = QLabel("Liking Settings")
        settings_title_lbl.setStyleSheet(
            "color: #FE2C55; font-weight: bold; font-size: 15px; background: transparent; border: none;"
        )
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.setFixedSize(50, 22)
        self.reset_btn.setStyleSheet("padding: 1px; font-size: 12px;")
        self.reset_btn.clicked.connect(self.reset_settings_to_default)
        settings_header.addWidget(settings_title_lbl)
        settings_header.addStretch()
        settings_header.addWidget(self.reset_btn)
        settings_container_layout.addLayout(settings_header)

        # Bordered box (same look as QGroupBox interior)
        settings_box = QFrame()
        settings_box.setObjectName("settings_box")
        settings_box.setStyleSheet(
            "QFrame#settings_box { border: 1px solid #333; border-radius: 8px; background-color: #1a1a1a; }"
        )
        settings_layout = QFormLayout(settings_box)
        settings_layout.setSpacing(12)
        settings_layout.setContentsMargins(10, 12, 10, 12)

        # Base Delay
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setRange(50, 500)
        self.delay_slider.setValue(self.settings.get("like_delay_ms", 50))
        self.delay_val_lbl = QLabel(f"{self.delay_slider.value()} ms")
        self.delay_val_lbl.setMinimumWidth(45)

        delay_layout = QHBoxLayout()
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(self.delay_val_lbl)

        self.delay_slider.valueChanged.connect(
            lambda v: (self.delay_val_lbl.setText(f"{v} ms"), self.save_settings_ui())
        )

        # Randomization
        self.rand_slider = QSlider(Qt.Orientation.Horizontal)
        self.rand_slider.setRange(0, 100)
        self.rand_slider.setValue(self.settings.get("randomization_ms", 50))
        self.rand_val_lbl = QLabel(f"{self.rand_slider.value()} ms")
        self.rand_val_lbl.setMinimumWidth(45)

        rand_layout = QHBoxLayout()
        rand_layout.addWidget(self.rand_slider)
        rand_layout.addWidget(self.rand_val_lbl)

        self.rand_slider.valueChanged.connect(
            lambda v: (self.rand_val_lbl.setText(f"{v} ms"), self.save_settings_ui())
        )

        settings_layout.addRow("Base Delay:", delay_layout)
        settings_layout.addRow("Randomization:", rand_layout)

        settings_container_layout.addWidget(settings_box)
        left_layout.addWidget(settings_container)
        
        # Update Banner (hidden by default, shown if a newer version is detected on GitHub)
        self.update_banner = QFrame()
        self.update_banner.setObjectName("update_banner")
        self.update_banner.setStyleSheet("""
            QFrame#update_banner {
                background-color: #15292b;
                border: 1px solid #25F4EE;
                border-radius: 6px;
            }
        """)
        banner_layout = QHBoxLayout(self.update_banner)
        banner_layout.setContentsMargins(8, 4, 8, 4)
        banner_layout.setSpacing(6)

        self.update_lbl = QLabel("🎉 Update available!")
        self.update_lbl.setStyleSheet("color: #25F4EE; font-weight: bold; font-size: 8.5pt; background: transparent; border: none;")

        self.download_btn = QPushButton("Download")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #25F4EE;
                color: #121212;
                border: none;
                border-radius: 4px;
                padding: 3px 8px;
                font-weight: bold;
                font-size: 8.5pt;
            }
            QPushButton:hover {
                background-color: #1fe0d9;
            }
        """)
        self.download_url = f"https://github.com/{GITHUB_REPO}/releases"
        self.download_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.download_url)))

        dismiss_btn = QPushButton("✕")
        dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dismiss_btn.setFixedSize(18, 18)
        dismiss_btn.setStyleSheet("color: #888; background: transparent; border: none; font-size: 8.5pt;")
        dismiss_btn.clicked.connect(self.update_banner.hide)

        banner_layout.addWidget(self.update_lbl)
        banner_layout.addStretch()
        banner_layout.addWidget(self.download_btn)
        banner_layout.addWidget(dismiss_btn)

        self.update_banner.hide()
        left_layout.addWidget(self.update_banner)

        self.status_label = QLabel("● Initializing...")
        self.status_label.setObjectName("status_label")
        self.status_label.setWordWrap(True)
        left_layout.addWidget(self.status_label)

        splitter.addWidget(left_panel)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
        
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(4)

        self.signout_btn = QPushButton("Sign Out")
        self.signout_btn.setToolTip("Sign out of your TikTok account")
        self.signout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signout_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #FF5A5A;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 8.5pt;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #382224;
                color: #FF7777;
                border-color: #552226;
            }
            QPushButton:pressed {
                background-color: #221516;
            }
        """)
        self.signout_btn.clicked.connect(self.sign_out)
        self.signout_btn.setVisible(False)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Refresh Active Tab")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FE2C55;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 8.5pt;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #E0284D;
            }
            QPushButton:pressed {
                background-color: #C12242;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_current_tab)

        corner_layout.addWidget(refresh_btn)
        corner_layout.addWidget(self.signout_btn)
        self.tabs.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
        
        splitter.addWidget(self.tabs)
        splitter.setSizes([350, 850])

    def _setup_webview_engine(self):
        self.waiting_webview = QtWebView2Widget(
            lazyload=False,
            user_data_folder="./userdata",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            init_settings_hook=self._on_waiting_core_init
        )
        self.waiting_webview.load_html(WAITING_HTML)
        self.status_label.setText("● Checking login status...")
        self._update_waiting_tab()

    def _on_waiting_core_init(self, core_wv2):
        QMetaObject.invokeMethod(self, "_start_auth_flow", Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def _start_auth_flow(self):
        self.login_webview = QtWebView2Widget(
            url="https://www.tiktok.com/login",
            lazyload=False,
            user_data_folder="./userdata",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            init_settings_hook=self._on_login_core_init
        )
        QTimer.singleShot(4500, self._reveal_login_tab)

    def _on_login_core_init(self, core_wv2):
        try:
            core_wv2.IsMuted = True
        except Exception:
            pass
            
        def on_source_changed(sender, args):
            url_str = sender.Source
            if "tiktok.com" in url_str and "login" not in url_str:
                QMetaObject.invokeMethod(self, "_on_login_success", Qt.ConnectionType.QueuedConnection)
        core_wv2.SourceChanged += on_source_changed

    def _on_explore_core_init(self, core_wv2):
        def on_source_changed(sender, args):
            url_str = sender.Source
            QTimer.singleShot(0, lambda: self._handle_explore_url(url_str))
        core_wv2.SourceChanged += on_source_changed

    def _handle_explore_url(self, url):
        if "tiktok.com/@" in url and "/live" in url:
            try:
                username = url.split("tiktok.com/@")[1].split("/")[0].split("?")[0]
                if username and username not in self.favorites:
                    self.search_input.setText(username)
            except Exception:
                pass

    def _update_floating_dot(self):
        if not getattr(self, 'floating_dot', None):
            return
            
        try:
            if getattr(self, 'waiting_webview', None) is None:
                return
            idx = self.tabs.indexOf(self.waiting_webview)
        except RuntimeError:
            return
            
        if idx != -1:
            rect = self.tabs.tabBar().tabRect(idx)
            fm = self.tabs.fontMetrics()
            
            full_text = "System Idle\u00A0\u00A0\u00A0\u00A0"
            base_text = "System Idle"
            
            full_width = fm.horizontalAdvance(full_text)
            base_width = fm.horizontalAdvance(base_text)
            
            # The full text block is perfectly centered in the tab rect
            text_start_x = rect.center().x() - (full_width / 2)
            
            # Place the dot precisely 6px after the base text
            dot_x = text_start_x + base_width + 6
            dot_y = rect.center().y() - 7
            
            self.floating_dot.move(int(dot_x), int(dot_y))
            self.floating_dot.show()
            self.floating_dot.raise_()
        else:
            self.floating_dot.hide()

    def _update_waiting_tab(self):
        if not hasattr(self, 'waiting_webview') or not self.waiting_webview:
            return
            
        idx = self.tabs.indexOf(self.waiting_webview)
        
        is_login_visible = False
        if getattr(self, 'login_webview', None) is not None:
            is_login_visible = self.tabs.indexOf(self.login_webview) != -1
            
        needs_waiting = len(self.active_streams) == 0 and not is_login_visible
        
        if needs_waiting and idx == -1:
            # 4 non-breaking spaces reserve exactly ~16px of space to balance the dot and gap
            new_idx = self.tabs.addTab(self.waiting_webview, "System Idle\u00A0\u00A0\u00A0\u00A0")
            
            if self.floating_dot is None:
                self.floating_dot = PulsingDot(self.tabs.tabBar())
            
            # Use a 0x0 widget instead of None to collapse the reserved close-button space
            self.tabs.tabBar().setTabButton(new_idx, self.tabs.tabBar().ButtonPosition.RightSide, self._get_zero_widget())
            
        elif not needs_waiting and idx != -1:
            self.tabs.removeTab(idx)

    @pyqtSlot()
    def _on_login_success(self):
        if self._has_handled_login:
            return
        self._has_handled_login = True
        
        self.is_logged_in = True
        if hasattr(self, 'signout_btn'):
            self.signout_btn.setVisible(True)
        self.status_label.setText("● Logged in! Monitoring favorites...")
        
        if self.login_webview is not None:
            idx = self.tabs.indexOf(self.login_webview)
            if idx != -1:
                self.tabs.removeTab(idx)
            self.login_webview.deleteLater()
            self.login_webview = None

        if self.explore_webview is None:
            current = self.tabs.currentWidget()
            self.explore_webview = QtWebView2Widget(
                url="https://www.tiktok.com/",
                lazyload=True,
                user_data_folder="./userdata",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                init_settings_hook=self._on_explore_core_init
            )
            self.tabs.insertTab(0, self.explore_webview, "Explore TikTok")
            self.tabs.tabBar().setTabButton(0, self.tabs.tabBar().ButtonPosition.RightSide, self._get_zero_widget())
            if current:
                self.tabs.setCurrentWidget(current)

        self._update_waiting_tab()
        self._start_monitoring()

    def _reveal_login_tab(self):
        if self.is_logged_in or getattr(self, 'login_webview', None) is None:
            return
        if hasattr(self, 'signout_btn'):
            self.signout_btn.setVisible(False)
        self.status_label.setText("● Not logged in. Please log in.")
        
        try:
            idx = self.tabs.indexOf(self.login_webview)
        except RuntimeError:
            return
            
        if idx == -1:
            idx = self.tabs.addTab(self.login_webview, "TikTok Login")
            self.tabs.setCurrentIndex(idx)
            self.tabs.tabBar().setTabButton(idx, self.tabs.tabBar().ButtonPosition.RightSide, None)
            self._update_waiting_tab()

    def _start_monitoring(self):
        if self.is_monitoring:
            return
        self.is_monitoring = True
        
        self.checker = LiveChecker()
        self.checker.status_checked.connect(self.on_live_status)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.trigger_check)
        self.check_timer.start(60000)
        
        QTimer.singleShot(2000, self.trigger_check)

    def refresh_current_tab(self):
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'reload'):
            current_widget.reload()
        elif hasattr(current_widget, 'webview') and hasattr(current_widget.webview, 'reload'):
            current_widget.webview.reload()

    def sign_out(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Sign Out")
        msg_box.setText("Are you sure you want to sign out of TikTok?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        yes_btn = msg_box.addButton(QMessageBox.StandardButton.Yes)
        no_btn = msg_box.addButton(QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(no_btn)
        
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        msg_box.exec()
        if msg_box.clickedButton() != yes_btn:
            return

        self.is_logged_in = False
        self._has_handled_login = False
        if hasattr(self, 'signout_btn'):
            self.signout_btn.setVisible(False)

        # Remove Explore tab if open
        if getattr(self, 'explore_webview', None) is not None:
            idx = self.tabs.indexOf(self.explore_webview)
            if idx != -1:
                self.tabs.removeTab(idx)
            self.explore_webview.close()
            self.explore_webview.deleteLater()
            self.explore_webview = None

        # Clean up existing login webview if present
        if getattr(self, 'login_webview', None) is not None:
            idx = self.tabs.indexOf(self.login_webview)
            if idx != -1:
                self.tabs.removeTab(idx)
            self.login_webview.close()
            self.login_webview.deleteLater()
            self.login_webview = None

        self.status_label.setText("● Signing out...")
        self.login_webview = QtWebView2Widget(
            url="https://www.tiktok.com/logout",
            lazyload=False,
            user_data_folder="./userdata",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            init_settings_hook=self._on_login_core_init
        )
        
        # After logout, redirect to /login and present login tab
        QTimer.singleShot(3000, lambda: getattr(self, 'login_webview', None) and self.login_webview.load_url("https://www.tiktok.com/login"))
        QTimer.singleShot(3500, self._reveal_login_tab)

    def add_favorite(self):
        username = self.search_input.text().strip().replace("@", "")
        if not username: return
        if username not in self.favorites:
            self.favorites[username] = True
            self._add_user_list_item(username)
            self._sort_list()
            SettingsManager.save_favorites(self.favorites)
            self.search_input.clear()
            self.status_label.setText(f"● Added {username} to favorites.")
            if self.is_monitoring:
                self.checker.check_users([username])
        else:
            QMessageBox.information(self, "Info", "User is already in favorites.")

    def remove_favorite(self, username=None):
        if username is None:
            return
            
        if username in self.favorites:
            if isinstance(self.favorites, list):
                self.favorites.remove(username)
            elif isinstance(self.favorites, dict):
                del self.favorites[username]
                
        # Find item in fav_list and remove it
        for i in range(self.fav_list.count()):
            item = self.fav_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == username:
                self.fav_list.takeItem(i)
                break
                
        if username in self.fav_widgets:
            del self.fav_widgets[username]
        SettingsManager.save_favorites(self.favorites)
        self.status_label.setText(f"● Removed {username} from favorites.")
        
        if username in self.active_streams:
            tab_idx = self.tabs.indexOf(self.active_streams[username])
            if tab_idx != -1:
                self.tabs.removeTab(tab_idx)
            self.active_streams[username].cleanup()
            self.active_streams[username].deleteLater()
            del self.active_streams[username]
            self._update_waiting_tab()
        
        self.checker.queue = [u for u in self.checker.queue if u != username]

    def save_settings_ui(self):
        self.settings["like_delay_ms"] = self.delay_slider.value()
        self.settings["randomization_ms"] = self.rand_slider.value()
        SettingsManager.save_settings(self.settings)
        
        for stream in self.active_streams.values():
            stream.update_settings(self.settings)
            
    def reset_settings_to_default(self):
        self.delay_slider.setValue(50)
        self.rand_slider.setValue(50)

    def check_for_updates(self, manual=False):
        """Asynchronously query GitHub Releases API for new version."""
        self._manual_update_check = manual
        url = QUrl(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")
        req = QNetworkRequest(url)
        req.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "TikTokLiveAutoLikerApp")
        reply = self.avatar_manager.get(req)
        reply.finished.connect(lambda: self._on_update_check_finished(reply))

    def _on_update_check_finished(self, reply):
        try:
            if reply.error() == QNetworkReply.NetworkError.NoError:
                data_bytes = reply.readAll().data()
                data = json.loads(data_bytes.decode('utf-8'))
                latest_tag = data.get("tag_name", "").strip()
                html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                
                if self._is_newer_version(APP_VERSION, latest_tag):
                    self.download_url = html_url
                    self.update_lbl.setText(f"🎉 Update available: {latest_tag}!")
                    self.update_banner.show()
                elif getattr(self, '_manual_update_check', False):
                    QMessageBox.information(self, "Update Check", f"You are using the latest version ({APP_VERSION}).")
            elif getattr(self, '_manual_update_check', False):
                QMessageBox.warning(self, "Update Check", "Could not check for updates. Please check your internet connection.")
        except Exception:
            pass
        finally:
            reply.deleteLater()

    @staticmethod
    def _is_newer_version(current, latest):
        import re
        def parse(v):
            cleaned = re.sub(r'[^0-9.]', '', str(v))
            parts = [int(p) for p in cleaned.split('.') if p.isdigit()]
            return tuple(parts) if parts else (0, 0, 0)
        return parse(latest) > parse(current)

    def trigger_check(self):
        users = list(self.favorites.keys())
        if not users:
            return
        self._pending_checks = len(users)
        self.status_label.setText(f"● Checking live status... (0/{self._pending_checks})")
        self.checker.check_users(users)

    def _update_status_label(self):
        total = len(self.favorites)
        live_count = len(getattr(self, 'known_live', set()))
        liking_count = sum(1 for t in self.active_streams.values() if getattr(t, 'tapper_enabled', False))
        self.status_label.setText(f"● Monitoring {total} users │ {live_count} live │ {liking_count} liking")

    # --- Sort constants ---
    _SORT_DEFAULT_REVERSE = {
        'name':   False,   # A → Z
        'live':   True,    # Live first
        'tapper': True,    # On first
        'mute':   False,   # Unmuted first
    }

    def _on_sort_clicked(self, key):
        """Cycle direction if already active; otherwise switch to new key with its default direction."""
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = self._SORT_DEFAULT_REVERSE[key]
        self._update_sort_buttons()
        self._sort_list()

    def _update_sort_buttons(self):
        """Refresh button labels and styles to reflect current sort state."""
        labels = {
            'name':   'Name',
            'live':   '\U0001f4e1 Live',
            'tapper': '\u2764 Tapper',
            'mute':   '\U0001f507 Mute',
        }
        active_style = (
            "QPushButton { background: #FE2C55; color: white; border: none; "
            "border-radius: 4px; padding: 1px 6px; font-size: 8.5pt; font-weight: bold; }"
        )
        inactive_style = (
            "QPushButton { background: #222; color: #666; border: 1px solid #333; "
            "border-radius: 4px; padding: 1px 6px; font-size: 8.5pt; } "
            "QPushButton:hover { background: #2e2e2e; color: #aaa; }"
        )
        for key, btn in self.sort_buttons.items():
            if key == self.sort_key:
                arrow = '\u25bc' if self.sort_reverse else '\u25b2'
                btn.setText(f"{labels[key]} {arrow}")
                btn.setStyleSheet(active_style)
            else:
                btn.setText(f"{labels[key]} \u21c5")
                btn.setStyleSheet(inactive_style)

    def _sort_list(self):
        """Re-order fav_list by clearing it and rebuilding in sorted order.

        Uses a clear+rebuild approach rather than takeItem/re-insert because
        setItemWidget transfers C++ ownership of the widget to the viewport;
        takeItem can leave those widget pointers dangling, causing a crash.
        """
        if not hasattr(self, 'sort_key') or not hasattr(self, 'fav_list'):
            return
        if getattr(self, '_rebuilding_sort', False):
            return  # Re-entry guard — we are already inside a rebuild
        count = self.fav_list.count()
        if count <= 1:
            return

        usernames = [
            self.fav_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(count)
        ]

        key = self.sort_key
        reverse = self.sort_reverse
        known_live = getattr(self, 'known_live', set())
        muted_map = self.settings.get("muted_users", {})

        def sort_key_fn(un):
            if key == 'name':   return un.lower()
            if key == 'live':   return un in known_live
            if key == 'tapper': return self.favorites.get(un, True)
            if key == 'mute':   return muted_map.get(un, True)
            return un.lower()

        sorted_usernames = sorted(usernames, key=sort_key_fn, reverse=reverse)
        if sorted_usernames == usernames:
            return  # Already in order — no rebuild needed

        self._rebuilding_sort = True
        try:
            self.fav_list.clear()       # Deletes old items; fresh widgets below
            self.fav_widgets.clear()
            for un in sorted_usernames:
                self._add_user_list_item(un)
            # Restore live/offline status badges on the fresh widgets
            for un in sorted_usernames:
                if un in self.fav_widgets:
                    self.fav_widgets[un].set_status(un in known_live)
        finally:
            self._rebuilding_sort = False

    def on_live_status(self, username, is_live, avatar_url="", is_error=False):
        if username not in self.favorites:
            return

        # Simple counter-based progress — immune to pool timing races
        total = getattr(self, '_pending_checks', 0)
        if total > 0:
            self._completed_checks = getattr(self, '_completed_checks', 0) + 1
            completed = self._completed_checks
            self.status_label.setText(f"● Checking live status... ({completed}/{total})")

        # If check resulted in a network/timeout error (even after retries), DO NOT alter state or close stream tabs
        if is_error:
            if total > 0 and getattr(self, '_completed_checks', 0) >= total:
                self._pending_checks = 0
                self._completed_checks = 0
                self._update_status_label()
            return

        if not hasattr(self, 'known_live'):
            self.known_live = set()
        if not hasattr(self, 'consecutive_offline'):
            self.consecutive_offline = {}

        if is_live:
            self.consecutive_offline[username] = 0
            self.known_live.add(username)
            if username in self.fav_widgets:
                self.fav_widgets[username].set_status(True)
                if avatar_url and getattr(self.fav_widgets[username], 'current_avatar_url', None) != avatar_url:
                    self.fav_widgets[username].current_avatar_url = avatar_url
                    self._download_avatar(username, avatar_url)

            self._sort_list()                  # Re-sort as each result arrives
            tapper_enabled = self.favorites.get(username, True)
            if username not in self.active_streams and tapper_enabled:
                is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
                tab = LiveTab(username, self.settings, tapper_enabled, is_muted)

                prefix = "❤️ " if tapper_enabled else ""
                idx = self.tabs.addTab(tab, f"{prefix}LIVE: @{username}")
                self.tabs.setCurrentIndex(idx)

                self.active_streams[username] = tab
                self._update_waiting_tab()
        else:
            # Increment consecutive offline counter
            self.consecutive_offline[username] = self.consecutive_offline.get(username, 0) + 1

            # Require 2 consecutive clean offline checks before marking offline & closing active stream tab
            if self.consecutive_offline[username] >= 2:
                self.known_live.discard(username)
                if username in self.fav_widgets:
                    self.fav_widgets[username].set_status(False)
                self._sort_list()                  # Re-sort as each result arrives

                if username in self.active_streams:
                    tab_idx = self.tabs.indexOf(self.active_streams[username])
                    if tab_idx != -1:
                        self.tabs.removeTab(tab_idx)
                    self.active_streams[username].cleanup()
                    self.active_streams[username].deleteLater()
                    del self.active_streams[username]
                    self._update_waiting_tab()

        # When all results are in, switch to the summary label
        if total > 0 and getattr(self, '_completed_checks', 0) >= total:
            self._pending_checks = 0
            self._completed_checks = 0
            self._update_status_label()

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if hasattr(self, 'login_webview') and widget == self.login_webview:
            return 
            
        if hasattr(self, 'waiting_webview') and widget == self.waiting_webview:
            return
            
        if hasattr(self, 'explore_webview') and widget == self.explore_webview:
            return
            
        for username, tab in list(self.active_streams.items()):
            if tab == widget:
                del self.active_streams[username]
                break
        
        self.tabs.removeTab(index)
        widget.cleanup()
        widget.deleteLater()
        self._update_waiting_tab()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qInstallMessageHandler(_qt_message_handler)
    app.setFont(QFont("Segoe UI", 10))
    window = TikTokAutoLikerApp()
    window.show()
    sys.exit(app.exec())
