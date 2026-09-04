import os
import sys

# Suppress C++ stderr console spam from QtWebEngine & QFont
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --log-level=3 --disable-gpu-memory-buffer-video-frames"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"

import json
import random
import shutil
import math
import time
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QSpinBox, QSlider,
    QTabWidget, QTabBar, QSplitter, QGroupBox, QFormLayout, QMessageBox, QListWidgetItem, QFrame, QFileDialog, QToolButton,
    QDialog, QComboBox, QCheckBox, QRadioButton, QButtonGroup, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject, pyqtSlot, QMetaObject, qInstallMessageHandler, QStandardPaths, QSize, QRect
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap, QPainterPath, QDesktopServices, QFont
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from webview_engine import UniversalWebView, get_best_engine_class
from sync_manager import SyncManager, FolderSyncBackend, WebDAVSyncBackend, RestSyncBackend
from stats_manager import StatsManager


def _qt_message_handler(mode, context, message):
    if "setPointSize" in message or "Point size" in message or "QFont" in message:
        return


APP_VERSION = "v1.1.3"
GITHUB_REPO = "Crypto90/TikTok-Live-Auto-Liker-Tapper"


def get_data_dir():
    """Resolve data directory: prefer existing local portable files, otherwise use OS standard app data."""
    if os.path.exists("favorites.json") or os.path.exists("settings.json") or os.path.exists("userdata"):
        return os.path.abspath(".")
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base or base.endswith("Application Support"):
        base = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation) or os.path.expanduser("~"), "TikTokLiveAutoLiker")
    elif not base.endswith("TikTokLiveAutoLiker"):
        base = os.path.join(base, "TikTokLiveAutoLiker")
    os.makedirs(base, exist_ok=True)
    return base


DATA_DIR = get_data_dir()
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
USER_DATA_DIR = os.path.join(DATA_DIR, "userdata")
AVATARS_DIR = os.path.join(DATA_DIR, "avatars")
os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)


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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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


def make_heart_icon(size=20, color_hex="#FE2C55"):
    target = QPixmap(size, size)
    target.fill(Qt.GlobalColor.transparent)
    painter = QPainter(target)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color_hex))

    s = size / 24.0
    path = QPainterPath()
    path.moveTo(12 * s, 21.35 * s)
    path.cubicTo(11.45 * s, 21.0 * s, 3.5 * s, 15.36 * s, 2.0 * s, 9.5 * s)
    path.cubicTo(1.0 * s, 5.5 * s, 4.0 * s, 2.5 * s, 8.0 * s, 2.5 * s)
    path.cubicTo(10.5 * s, 2.5 * s, 11.5 * s, 4.0 * s, 12.0 * s, 5.0 * s)
    path.cubicTo(12.5 * s, 4.0 * s, 13.5 * s, 2.5 * s, 16.0 * s, 2.5 * s)
    path.cubicTo(20.0 * s, 2.5 * s, 23.0 * s, 5.5 * s, 22.0 * s, 9.5 * s)
    path.cubicTo(20.5 * s, 15.36 * s, 12.55 * s, 21.0 * s, 12 * s, 21.35 * s)
    painter.drawPath(path)
    painter.end()
    return target


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
        self.toggle_btn = QToolButton()
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_tapper_enabled(is_enabled)

        # Mute Toggle Button
        self.mute_btn = QToolButton()
        self.mute_btn.setFixedSize(28, 28)
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_muted(is_muted)

        # Delete Button
        self.del_btn = QToolButton()
        self.del_btn.setFixedSize(28, 28)
        self.del_btn.setText("❌")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QToolButton {
                color: #888;
                background: transparent;
                border: none;
                border-radius: 14px;
                font-size: 13pt;
            }
            QToolButton:hover {
                background-color: rgba(255, 90, 90, 0.15);
                color: #FF5A5A;
            }
        """)

        layout.addWidget(self.avatar_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.mute_btn)
        layout.addWidget(self.del_btn)

    def set_tapper_enabled(self, is_enabled):
        color = "#FE2C55" if is_enabled else "#555555"
        self.toggle_btn.setIcon(QIcon(make_heart_icon(20, color)))
        self.toggle_btn.setIconSize(QSize(20, 20))
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 14px;
            }
            QToolButton:hover {
                background-color: rgba(254, 44, 85, 0.15);
            }
        """)
        self.toggle_btn.setToolTip("Auto-Tapper: ON" if is_enabled else "Auto-Tapper: OFF")

    def set_muted(self, muted):
        if muted:
            self.mute_btn.setText("🔇")
            self.mute_btn.setStyleSheet("""
                QToolButton {
                    color: #888;
                    background: transparent;
                    border: none;
                    border-radius: 14px;
                    font-size: 15pt;
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.08);
                }
            """)
            self.mute_btn.setToolTip("Muted")
        else:
            self.mute_btn.setText("🔊")
            self.mute_btn.setStyleSheet("""
                QToolButton {
                    color: #4CAF50;
                    background: transparent;
                    border: none;
                    border-radius: 14px;
                    font-size: 15pt;
                }
                QToolButton:hover {
                    background-color: rgba(76, 175, 80, 0.15);
                }
            """)
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
            except Exception:
                pass
        return {}

    @staticmethod
    def save_favorites(favorites):
        try:
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f, indent=2)
        except Exception:
            pass

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
            except Exception:
                pass
        return default_settings

    @staticmethod
    def save_settings(settings):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass


class CheckerWorker(QObject):
    status_checked = pyqtSignal(str, bool, str, bool)  # (username, is_live, avatar_url, is_error)
    ready = pyqtSignal(object)

    TIMEOUT_MS = 25000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.webview = UniversalWebView(
            parent=None,
            user_data_folder=USER_DATA_DIR,
            is_headless=True
        )
        self.webview.set_muted(True)
        self.webview.navigation_completed.connect(self._on_nav_completed)

        self.current_user = None
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
        if self._done:
            return
        self._done = True
        self._watchdog.stop()
        self.status_checked.emit(self.current_user, bool(is_live), str(avatar_url), bool(is_error))
        self.ready.emit(self)

    @pyqtSlot()
    def _on_timeout(self):
        self._finish(False, "", is_error=True)

    def _on_nav_completed(self, is_success, url):
        if not is_success:
            self._finish(False, "", is_error=True)
            return

        current_lower = str(self.current_user or "").lower()
        url_lower = str(url or "").lower()
        if "/live" not in url_lower and f"@{current_lower}" in url_lower:
            QTimer.singleShot(2500, lambda s=self: QMetaObject.invokeMethod(
                s, "_check_profile_avatar_js", Qt.ConnectionType.QueuedConnection
            ))
            return

        QTimer.singleShot(3500, lambda s=self: QMetaObject.invokeMethod(
            s, "_check_js", Qt.ConnectionType.QueuedConnection
        ))

    @pyqtSlot()
    def _check_profile_avatar_js(self):
        if self._done:
            return
        js_code = """(function() {
            var img = document.querySelector('img[data-e2e="user-avatar"]')
                   || document.querySelector('img[class*="Avatar"], img[class*="avatar"]');
            return { avatar_url: img ? img.src : '' };
        })();"""
        self.webview.evaluate_js(js_code, self._on_profile_avatar_result)

    def _on_profile_avatar_result(self, result_dict):
        res = result_dict.get('result')
        if isinstance(res, dict) or hasattr(res, 'get'):
            data = res
        elif isinstance(res, str):
            try: data = json.loads(res)
            except Exception: data = {}
        else:
            data = {}
        avatar_url = str(data.get('avatar_url', '') or '')
        self._finish(False, avatar_url, is_error=False)

    @pyqtSlot()
    def _check_js(self):
        if self._done:
            return
        js_code = """(function() {
            var isLiveUrl = window.location.href.indexOf('/live') !== -1;
            var video = document.querySelector('video') !== null || 
                        document.querySelector('[data-e2e="live-video"]') !== null ||
                        document.querySelector('.tiktok-web-player') !== null;
            var img = document.querySelector('img[data-e2e="user-avatar"]') ||
                      document.querySelector('img[class*="Avatar"], img[class*="avatar"]');
            var avatar = img ? img.src : '';
            var endOverlay = document.querySelector('[data-e2e="live-end-card"], [data-e2e="live-end-follow"]') !== null;
            var bodyText = document.body ? document.body.innerText : '';
            var ended = endOverlay || /live.has.ended|stream.ended|broadcast.ended|replay|ist zu ende|ha terminado|a pris fin|è terminat/i.test(bodyText);
            return { is_live: isLiveUrl && video && !ended, avatar_url: avatar };
        })();"""
        self.webview.evaluate_js(js_code, self._on_js_result)

    def _on_js_result(self, result_dict):
        res = result_dict.get('result')
        if isinstance(res, dict) or hasattr(res, 'get'):
            data = res
        elif isinstance(res, str):
            try: data = json.loads(res)
            except Exception: data = {}
        else:
            data = {}
        is_live = bool(data.get('is_live', False))
        avatar_url = str(data.get('avatar_url', '') or '')
        self._finish(is_live, avatar_url, is_error=False)

    def cleanup(self):
        self._watchdog.stop()
        if getattr(self, 'webview', None):
            self.webview.cleanup()
            self.webview.deleteLater()
            self.webview = None


class LiveChecker(QObject):
    status_checked = pyqtSignal(str, bool, str, bool)

    def __init__(self, pool_size=2, max_retries=2):
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
        if not users:
            return
        for u in users:
            self.retry_counts[u] = 0
            if u not in self.queue:
                self.queue.append(u)
        self._process_queue()

    def _on_worker_status(self, username, is_live, avatar_url, is_error):
        if is_error and self.retry_counts.get(username, 0) < self.max_retries:
            self.retry_counts[username] += 1
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
            worker.cleanup()
        self.workers.clear()
        self.idle_workers.clear()
        self.queue.clear()


class LiveTab(QWidget):
    stream_ended = pyqtSignal(str, str)

    # Recycle threshold: after 60 minutes, reload the stream to clear caches
    _RECYCLE_THRESHOLD_S = 60 * 60

    def __init__(self, username, settings, tapper_enabled=True, is_muted=True, stats_mgr=None, tabs_widget=None):
        super().__init__()
        self.username = username
        self.settings = settings
        self.tapper_enabled = tapper_enabled
        self.is_muted = is_muted
        self.stats_mgr = stats_mgr
        self.tabs_widget = tabs_widget
        self.session_id = None
        self._is_background = False
        self._stream_end_detected = False
        self._tab_opened_at = time.time()
        self._last_stats_tick = time.time()
        self._last_verified = 0
        self._last_dispatched = 0
        self._live_rate = 0.0

        # Stream health tracking
        self._last_video_time = -1.0
        self._stall_count = 0
        self._STALL_THRESHOLD = 3

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sleek In-Tab Live Stats Bar Overlay
        self.stats_bar = QWidget(self)
        self.stats_bar.setFixedHeight(34)
        self.stats_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1a24, stop:1 #13131c);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        sb_layout = QHBoxLayout(self.stats_bar)
        sb_layout.setContentsMargins(12, 0, 12, 0)
        sb_layout.setSpacing(16)

        self.lbl_user = QLabel(f"<b>@{self.username}</b>", self.stats_bar)
        self.lbl_user.setStyleSheet("color: #00f2fe; font-size: 12px;")
        sb_layout.addWidget(self.lbl_user)

        self.lbl_verified = QLabel("❤️ Verified: <b>0</b>", self.stats_bar)
        self.lbl_verified.setStyleSheet("color: #ff2d55;")
        sb_layout.addWidget(self.lbl_verified)

        self.lbl_rate = QLabel("⚡ <b>0.0/s</b>", self.stats_bar)
        self.lbl_rate.setStyleSheet("color: #ffcc00;")
        sb_layout.addWidget(self.lbl_rate)

        self.lbl_timer = QLabel("⏱️ <b>00:00</b>", self.stats_bar)
        sb_layout.addWidget(self.lbl_timer)

        self.lbl_confirmed = QLabel("📶 <b>100% Confirmed</b>", self.stats_bar)
        self.lbl_confirmed.setStyleSheet("color: #2ed573;")
        sb_layout.addWidget(self.lbl_confirmed)

        sb_layout.addStretch()
        layout.addWidget(self.stats_bar)

        self.webview = UniversalWebView(
            parent=self,
            url=f"https://www.tiktok.com/@{self.username}/live",
            user_data_folder=USER_DATA_DIR
        )
        self.webview.set_muted(self.is_muted)
        self.webview.source_changed.connect(self._check_url_redirect)
        self.webview.navigation_completed.connect(self._on_nav_completed)
        layout.addWidget(self.webview)

        # 1-second live stats polling timer
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._poll_stats)
        self._stats_timer.start(1000)

        # Stream health monitor — checks every 15s for stream end/stall/redirect
        self._health_timer = QTimer(self)
        self._health_timer.timeout.connect(self._check_stream_health_js)
        self._health_timer.start(15000)

        # Periodic memory pressure relief / recycle check every 5 min
        self._recycle_timer = QTimer(self)
        self._recycle_timer.timeout.connect(self._recycle_if_stale)
        self._recycle_timer.start(300000)

    def _poll_stats(self):
        if not self._stream_end_detected:
            self.webview.get_tapper_stats(self._on_tapper_stats_result)

    def _on_tapper_stats_result(self, result_dict):
        res = result_dict.get('result')
        if isinstance(res, str):
            try: res = json.loads(res)
            except Exception: res = {}
        if not isinstance(res, dict):
            return

        dispatched = int(res.get('dispatched', 0) or 0)
        verified = int(res.get('verified', 0) or 0)
        failed = int(res.get('failed', 0) or 0)
        room_likes = int(res.get('roomLikes', 0) or 0)

        # Calculate live rate
        now = time.time()
        dt = max(0.5, now - self._last_stats_tick)
        delta_v = max(0, verified - self._last_verified)
        delta_d = max(0, dispatched - self._last_dispatched)
        if delta_v > 0:
            self._live_rate = round(delta_v / dt, 1)
        elif delta_d > 0:
            self._live_rate = round(delta_d / dt, 1)
        else:
            self._live_rate = 0.0

        self._last_stats_tick = now
        self._last_verified = verified
        self._last_dispatched = dispatched

        # Format session duration
        elapsed = int(now - self._tab_opened_at)
        mins, secs = divmod(elapsed, 60)
        hrs, mins = divmod(mins, 60)
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

        # Update stats bar labels
        self.lbl_verified.setText(f"❤️ Verified: <b>{verified:,}</b>")
        self.lbl_rate.setText(f"⚡ <b>{self._live_rate}/s</b>")
        self.lbl_timer.setText(f"⏱️ <b>{time_str}</b>")

        rate_pct = round((verified / max(1, dispatched)) * 100.0, 1) if dispatched > 0 else 100.0
        self.lbl_confirmed.setText(f"📶 <b>{rate_pct}% Confirmed</b>")

        # Update tab text dynamically
        if self.tabs_widget:
            idx = self.tabs_widget.indexOf(self)
            if idx != -1:
                prefix = "❤️ " if self.tapper_enabled else ""
                count_str = f" (❤️ {verified:,})" if verified > 0 else ""
                self.tabs_widget.setTabText(idx, f"{prefix}LIVE: @{self.username}{count_str}")

        # Update StatsManager session
        if self.stats_mgr and self.session_id:
            self.stats_mgr.record_progress(self.session_id, verified, dispatched, failed, room_likes)

    def _on_nav_completed(self, success, url):
        if success:
            self.webview.set_muted(self.is_muted)
            # Ensure video playback is unpaused natively
            self.webview.evaluate_js("(function() { var v = document.querySelector('video'); if (v && v.paused) v.play().catch(function(){}); })();")
            base = self.settings.get("like_delay_ms", 100)
            rand = self.settings.get("randomization_ms", 50)
            # Inject and start in-page native auto-tapper loop
            self.webview.inject_in_page_tapper(base, rand, enabled=self.tapper_enabled)

            # Start tracking in StatsManager
            if self.stats_mgr and not self.session_id:
                self.session_id = self.stats_mgr.start_session(self.username)

    def _check_url_redirect(self, url):
        if self._stream_end_detected:
            return
        expected = f"tiktok.com/@{self.username}/live"
        if url and "tiktok.com/@" in url and "/live" in url and expected.lower() not in url.lower():
            self._signal_stream_ended("redirected_to_other_streamer")
        elif url and "tiktok.com/@" in url and "/live" not in url:
            self._signal_stream_ended("redirected_away_from_live")

    def set_muted(self, muted):
        self.is_muted = muted
        self.webview.set_muted(muted)

    def set_tapper_enabled(self, enabled):
        self.tapper_enabled = enabled
        self.webview.set_tapper_enabled(enabled)

    def update_settings(self, settings):
        self.settings = settings
        base = self.settings.get("like_delay_ms", 100)
        rand = self.settings.get("randomization_ms", 50)
        self.webview.set_tapper_rate(base, rand)

    # --- Stream Health Monitor ---

    def _check_stream_health_js(self):
        if self._stream_end_detected:
            return
        js_code = """(function() {
            var signals = {};
            var video = document.querySelector('video');
            signals.has_video = !!video;
            signals.video_paused = video ? video.paused : true;
            signals.video_ended = video ? video.ended : true;
            signals.video_current_time = video ? video.currentTime : 0;
            signals.video_ready_state = video ? video.readyState : 0;

            var body_text = document.body ? document.body.innerText : '';
            signals.has_ended_text = /live.has.ended|stream.ended|broadcast.ended|replay|this live has ended|host.has.ended|ist zu ende|ha terminado|a pris fin|è terminat/i.test(body_text);
            signals.has_follow_overlay = !!document.querySelector('[data-e2e="live-end-follow"], [data-e2e="live-end-card"]');
            signals.current_url = window.location.href;
            return signals;
        })();"""
        self.webview.evaluate_js(js_code, self._on_stream_health_result)

    def _on_stream_health_result(self, result_dict):
        if self._stream_end_detected:
            return
        res = result_dict.get('result')
        if isinstance(res, dict) or hasattr(res, 'get'):
            signals = res
        elif isinstance(res, str):
            try: signals = json.loads(res)
            except Exception: return
        else:
            return

        if signals.get('has_ended_text', False) or signals.get('has_follow_overlay', False):
            self._signal_stream_ended("stream_ended_overlay")
            return

        current_url = signals.get('current_url', '')
        expected = f"tiktok.com/@{self.username}/live"
        if current_url:
            if "tiktok.com/@" in current_url and "/live" in current_url and expected.lower() not in current_url.lower():
                self._signal_stream_ended("redirected_to_other_streamer")
                return
            if "tiktok.com/@" in current_url and "/live" not in current_url:
                self._signal_stream_ended("redirected_away_from_live")
                return

        if not signals.get('has_video', False):
            self._stall_count += 1
            if self._stall_count >= self._STALL_THRESHOLD:
                self._signal_stream_ended("no_video_element")
            return

        video_time = signals.get('video_current_time', 0)
        if signals.get('video_ended', False):
            self._signal_stream_ended("video_ended_event")
            return

        if not signals.get('video_paused', False):
            if self._last_video_time >= 0 and abs(video_time - self._last_video_time) < 0.1:
                self._stall_count += 1
                if self._stall_count >= self._STALL_THRESHOLD:
                    self._signal_stream_ended("video_stalled")
                    return
            else:
                self._stall_count = 0
        self._last_video_time = video_time

    def _signal_stream_ended(self, reason):
        if self._stream_end_detected:
            return
        self._stream_end_detected = True
        self._health_timer.stop()
        if hasattr(self, '_stats_timer'):
            self._stats_timer.stop()
        self.webview.stop_tapper()
        if self.stats_mgr and self.session_id:
            self.stats_mgr.end_session(self.session_id, reason=reason)
            self.session_id = None
        self.stream_ended.emit(self.username, reason)

    def set_background_mode(self, is_background):
        if is_background == self._is_background:
            return
        self._is_background = is_background
        self.webview.set_background_mode(is_background)

    def _recycle_if_stale(self):
        if self._stream_end_detected:
            return
        elapsed = time.time() - self._tab_opened_at
        if elapsed < self._RECYCLE_THRESHOLD_S:
            return

        self._tab_opened_at = time.time()
        self._last_video_time = -1.0
        self._stall_count = 0
        try:
            self.webview.load_url(f"https://www.tiktok.com/@{self.username}/live")
        except Exception:
            pass

    def cleanup(self):
        self._health_timer.stop()
        if hasattr(self, '_stats_timer'):
            self._stats_timer.stop()
        if hasattr(self, '_recycle_timer'):
            self._recycle_timer.stop()
        if self.stats_mgr and self.session_id:
            self.stats_mgr.end_session(self.session_id, reason="closed")
            self.session_id = None
        self.webview.stop_tapper()
        self.webview.cleanup()
        self.webview.deleteLater()


class PulsingTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waiting_tab = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(100)
        self._start_time = time.time()
        self._opacity = 1.0

    def _animate(self):
        elapsed = time.time() - self._start_time
        self._opacity = 0.3 + 0.7 * ((math.sin(elapsed * 4.0) + 1) / 2)
        idx = self._get_waiting_idx()
        if idx != -1:
            self.update(self.tabRect(idx))

    def _get_waiting_idx(self):
        if not self.waiting_tab or not self.parent():
            return -1
        try:
            return self.parent().indexOf(self.waiting_tab)
        except Exception:
            return -1

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        if index == self._get_waiting_idx():
            fm = self.fontMetrics()
            tw = fm.horizontalAdvance("System Idle")
            # 69px text + 6px gap + 8px dot + 40px padding (20px left + 20px right)
            return QSize(tw + 6 + 8 + 40, size.height())
        return size

    def paintEvent(self, event):
        super().paintEvent(event)
        idx = self._get_waiting_idx()
        if idx != -1 and idx < self.count():
            rect = self.tabRect(idx)
            text = "System Idle"
            fm = self.fontMetrics()
            tw = fm.horizontalAdvance(text)
            dot_w = 8
            gap = 6
            total_w = tw + gap + dot_w

            # Center the combined (text + gap + dot) block perfectly inside rect
            start_x = rect.x() + (rect.width() - total_w) / 2
            text_x = start_x
            dot_x = start_x + tw + gap
            dot_y = rect.center().y() - dot_w / 2

            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setFont(self.font())

            is_selected = (self.currentIndex() == idx)
            text_color = QColor("#ffffff" if is_selected else "#888888")
            p.setPen(text_color)

            text_rect = QRect(int(text_x), rect.y(), int(tw), rect.height())
            p.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)

            c = QColor("#FE2C55")
            c.setAlphaF(self._opacity)
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(dot_x), int(dot_y), dot_w, dot_w)
            p.end()


class AnalyticsDialog(QDialog):
    """Modern dark analytics and statistics dialog for verified likes and sessions."""
    def __init__(self, stats_mgr, parent=None):
        super().__init__(parent)
        self.stats_mgr = stats_mgr
        self.setWindowTitle("📊 Stream Analytics & Verified Likes")
        self.resize(800, 580)
        self.setMinimumSize(680, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #12131a;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #232535;
                border-radius: 8px;
                background-color: #171822;
            }
            QTabBar::tab {
                background-color: #1f202e;
                color: #8c8ea6;
                padding: 8px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #171822;
                color: #25F4EE;
                border-bottom: 2px solid #25F4EE;
            }
            QTableWidget {
                background-color: #171822;
                border: none;
                color: #e0e0e0;
                gridline-color: #232535;
                selection-background-color: #2b2d40;
            }
            QHeaderView::section {
                background-color: #1b1c28;
                color: #8c8ea6;
                padding: 6px;
                border: 1px solid #232535;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header bar
        header_layout = QHBoxLayout()
        title_lbl = QLabel("📊 Stream Analytics & Verified Likes")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        export_btn = QPushButton("📥 Export CSV")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #25F4EE;
                color: #121212;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1dd2cd; }
        """)
        export_btn.clicked.connect(self._export_csv)
        header_layout.addWidget(export_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #232535;
                color: #e0e0e0;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #2e3045; }
        """)
        refresh_btn.clicked.connect(self._populate_data)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # KPI Metric Cards
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(12)

        self.card_likes = self._create_card("❤️ Verified Likes", "0", "#ff2d55")
        self.card_taps = self._create_card("👆 Taps Dispatched", "0", "#00f2fe")
        self.card_time = self._create_card("⏱️ Watch Time", "0m", "#ffcc00")
        self.card_rate = self._create_card("📶 Delivery Rate", "100%", "#2ed573")

        self.kpi_layout.addWidget(self.card_likes)
        self.kpi_layout.addWidget(self.card_taps)
        self.kpi_layout.addWidget(self.card_time)
        self.kpi_layout.addWidget(self.card_rate)
        layout.addLayout(self.kpi_layout)

        # Tabs
        self.tabs = QTabWidget(self)

        # Tab 1: Leaderboard
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(6)
        self.leaderboard_table.setHorizontalHeaderLabels(["Rank", "Streamer", "Verified Likes", "Taps Dispatched", "Delivery Rate", "Sessions"])
        self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.leaderboard_table.verticalHeader().setVisible(False)
        self.tabs.addTab(self.leaderboard_table, "🏆 Top Creators Leaderboard")

        # Tab 2: Sessions History
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(["Date & Time", "Streamer", "Duration", "Verified Likes", "Taps Dispatched", "Status"])
        self.sessions_table.horizontalHeader().setStretchLastSection(True)
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.sessions_table.verticalHeader().setVisible(False)
        self.tabs.addTab(self.sessions_table, "📜 Stream Sessions History")

        layout.addWidget(self.tabs)

        # Close button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #232535;
                color: #ffffff;
                padding: 6px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #2e3045; }
        """)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

        self._populate_data()

    def _create_card(self, title: str, val: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #171822;
                border: 1px solid #232535;
                border-radius: 8px;
            }
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(12, 10, 12, 10)
        l.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet("font-size: 11px; color: #8c8ea6; font-weight: 500;")
        v = QLabel(val)
        v.setObjectName("val_lbl")
        v.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def _update_card(self, card: QFrame, val: str):
        lbl = card.findChild(QLabel, "val_lbl")
        if lbl:
            lbl.setText(val)

    def _populate_data(self):
        if not self.stats_mgr:
            return
        kpis = self.stats_mgr.get_kpis()
        self._update_card(self.card_likes, f"{kpis['total_verified_likes']:,}")
        self._update_card(self.card_taps, f"{kpis['total_taps_dispatched']:,}")

        # Format total duration
        secs = kpis['total_duration_seconds']
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        dur_str = f"{h}h {m}m" if h > 0 else f"{m}m {s}s"
        self._update_card(self.card_time, dur_str)
        self._update_card(self.card_rate, f"{kpis['confirmation_rate_pct']}%")

        # Populate Leaderboard
        leaders = self.stats_mgr.get_streamer_leaderboard(limit=50)
        self.leaderboard_table.setRowCount(len(leaders))
        for row, l in enumerate(leaders):
            rank_str = "🥇" if row == 0 else ("🥈" if row == 1 else ("🥉" if row == 2 else f"#{row+1}"))
            self.leaderboard_table.setItem(row, 0, QTableWidgetItem(rank_str))
            self.leaderboard_table.setItem(row, 1, QTableWidgetItem(f"@{l['username']}"))
            self.leaderboard_table.setItem(row, 2, QTableWidgetItem(f"❤️ {l['verified_likes']:,}"))
            self.leaderboard_table.setItem(row, 3, QTableWidgetItem(f"{l['taps_dispatched']:,}"))
            self.leaderboard_table.setItem(row, 4, QTableWidgetItem(f"{l['confirmation_rate']}%"))
            self.leaderboard_table.setItem(row, 5, QTableWidgetItem(str(l['sessions_count'])))

        # Populate Sessions
        sessions = self.stats_mgr.get_recent_sessions(limit=100)
        self.sessions_table.setRowCount(len(sessions))
        for row, s in enumerate(sessions):
            st = s.get('started_at', 0)
            date_str = datetime.fromtimestamp(st, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if st else "-"
            dur_s = s.get('duration_seconds', 0)
            dm, ds = divmod(dur_s, 60)
            dh, dm = divmod(dm, 60)
            d_str = f"{dh}h {dm}m" if dh > 0 else f"{dm}m {ds}s"

            self.sessions_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(f"@{s.get('username', '')}"))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(d_str))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(f"❤️ {s.get('verified_likes', 0):,}"))
            self.sessions_table.setItem(row, 4, QTableWidgetItem(f"{s.get('taps_dispatched', 0):,}"))
            status_str = "🟢 Active" if s.get('status') == 'active' else s.get('status', 'completed').capitalize()
            self.sessions_table.setItem(row, 5, QTableWidgetItem(status_str))

    def _export_csv(self):
        if not self.stats_mgr:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Session Analytics CSV", "stream_analytics.csv", "CSV Files (*.csv)")
        if path:
            try:
                csv_data = self.stats_mgr.export_csv()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(csv_data)
                QMessageBox.information(self, "Export Successful", f"Analytics data successfully exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {e}")


class SyncSettingsDialog(QDialog):
    def __init__(self, parent=None, sync_manager=None, settings=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.settings = settings or {}
        self.setWindowTitle("Cloud & Multi-Device Sync")
        self.setFixedSize(540, 560)
        self.setStyleSheet("""
            QDialog {
                background-color: #16181f;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #282e3d;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #25F4EE;
            }
            QLineEdit, QComboBox {
                background-color: #1f2533;
                border: 1px solid #2d3648;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
                font-size: 9pt;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #FE2C55;
            }
            QPushButton {
                background-color: #252c3c;
                color: #ffffff;
                border: 1px solid #364057;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 8.5pt;
            }
            QPushButton:hover {
                background-color: #2f384d;
                border-color: #455370;
            }
            QPushButton#primaryBtn {
                background-color: #FE2C55;
                color: #ffffff;
                border: none;
            }
            QPushButton#primaryBtn:hover {
                background-color: #e01740;
            }
            QRadioButton, QCheckBox {
                color: #e0e0e0;
                font-size: 9pt;
            }
            QRadioButton::indicator:checked, QCheckBox::indicator:checked {
                background-color: #FE2C55;
                border: 1px solid #FE2C55;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        header_lbl = QLabel("Multi-Device Synchronization")
        header_lbl.setStyleSheet("font-size: 13pt; font-weight: bold; color: #ffffff;")
        sub_lbl = QLabel("Keep favorites, settings, and tapper toggles in sync across all your PCs and Linux servers.")
        sub_lbl.setStyleSheet("font-size: 8.5pt; color: #8c96a8;")
        sub_lbl.setWordWrap(True)
        layout.addWidget(header_lbl)
        layout.addWidget(sub_lbl)

        sync_cfg = self.settings.setdefault("sync", {})

        self.enable_cb = QCheckBox("Enable Automatic Cloud Sync")
        self.enable_cb.setChecked(bool(sync_cfg.get("enabled", False)))
        self.enable_cb.setStyleSheet("font-weight: bold; font-size: 9.5pt; color: #25F4EE;")
        layout.addWidget(self.enable_cb)

        method_box = QGroupBox("Sync Method")
        method_layout = QVBoxLayout(method_box)
        method_layout.setSpacing(8)

        self.btn_group = QButtonGroup(self)
        self.rb_folder = QRadioButton("📁 Shared Folder / Cloud Drive (Dropbox, OneDrive, Syncthing, LAN)")
        self.rb_webdav = QRadioButton("🌐 WebDAV Remote Server (Nextcloud, ownCloud, Fastmail)")
        self.rb_rest = QRadioButton("⚡ REST API Server (Self-hosted sync_server.py or Cloud)")

        self.btn_group.addButton(self.rb_folder, 1)
        self.btn_group.addButton(self.rb_webdav, 2)
        self.btn_group.addButton(self.rb_rest, 3)

        method = sync_cfg.get("method", "folder")
        if method == "webdav":
            self.rb_webdav.setChecked(True)
        elif method == "rest":
            self.rb_rest.setChecked(True)
        else:
            self.rb_folder.setChecked(True)

        method_layout.addWidget(self.rb_folder)
        method_layout.addWidget(self.rb_webdav)
        method_layout.addWidget(self.rb_rest)
        layout.addWidget(method_box)

        self.stack = QStackedWidget()

        # 1. Folder page
        folder_page = QWidget()
        f_layout = QVBoxLayout(folder_page)
        f_layout.setContentsMargins(0, 4, 0, 0)
        f_layout.setSpacing(6)
        f_lbl = QLabel("Shared Directory Path:")
        f_lbl.setStyleSheet("font-size: 8.5pt; color: #aaa;")
        f_row = QHBoxLayout()
        self.folder_edit = QLineEdit(sync_cfg.get("folder_path", ""))
        self.folder_edit.setPlaceholderText("Select folder in Dropbox, OneDrive, Syncthing, or SMB share")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_folder)
        f_row.addWidget(self.folder_edit)
        f_row.addWidget(browse_btn)
        f_hint = QLabel("💡 Tip: Selecting a folder in Dropbox, OneDrive, or Syncthing keeps all PCs in sync with zero setup!")
        f_hint.setStyleSheet("font-size: 7.5pt; color: #667; font-style: italic;")
        f_hint.setWordWrap(True)
        f_layout.addWidget(f_lbl)
        f_layout.addLayout(f_row)
        f_layout.addWidget(f_hint)
        f_layout.addStretch()
        self.stack.addWidget(folder_page)

        # 2. WebDAV page
        webdav_page = QWidget()
        w_layout = QFormLayout(webdav_page)
        w_layout.setContentsMargins(0, 4, 0, 0)
        w_layout.setSpacing(6)
        self.webdav_url_edit = QLineEdit(sync_cfg.get("webdav_url", ""))
        self.webdav_url_edit.setPlaceholderText("https://nextcloud.example.com/remote.php/dav/files/user/sync/")
        self.webdav_user_edit = QLineEdit(sync_cfg.get("webdav_username", ""))
        self.webdav_user_edit.setPlaceholderText("Username or email")
        self.webdav_pass_edit = QLineEdit(sync_cfg.get("webdav_password", ""))
        self.webdav_pass_edit.setPlaceholderText("App Password or Token")
        self.webdav_pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        w_layout.addRow("WebDAV URL:", self.webdav_url_edit)
        w_layout.addRow("Username:", self.webdav_user_edit)
        w_layout.addRow("Password:", self.webdav_pass_edit)
        self.stack.addWidget(webdav_page)

        # 3. REST page
        rest_page = QWidget()
        r_layout = QFormLayout(rest_page)
        r_layout.setContentsMargins(0, 4, 0, 0)
        r_layout.setSpacing(6)
        self.rest_url_edit = QLineEdit(sync_cfg.get("rest_url", ""))
        self.rest_url_edit.setPlaceholderText("http://your-server-ip:8765")
        self.rest_key_edit = QLineEdit(sync_cfg.get("rest_api_key", ""))
        self.rest_key_edit.setPlaceholderText("Optional secret API key")
        self.rest_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        r_layout.addRow("Server URL:", self.rest_url_edit)
        r_layout.addRow("API Key:", self.rest_key_edit)
        self.stack.addWidget(rest_page)

        layout.addWidget(self.stack)

        self.rb_folder.toggled.connect(lambda c: c and self.stack.setCurrentIndex(0))
        self.rb_webdav.toggled.connect(lambda c: c and self.stack.setCurrentIndex(1))
        self.rb_rest.toggled.connect(lambda c: c and self.stack.setCurrentIndex(2))
        if method == "webdav": self.stack.setCurrentIndex(1)
        elif method == "rest": self.stack.setCurrentIndex(2)
        else: self.stack.setCurrentIndex(0)

        int_row = QHBoxLayout()
        int_lbl = QLabel("Auto-Sync Interval:")
        int_lbl.setStyleSheet("font-size: 8.5pt; color: #aaa;")
        self.interval_combo = QComboBox()
        self.interval_combo.addItem("Every 30 seconds", 30)
        self.interval_combo.addItem("Every 60 seconds (Recommended)", 60)
        self.interval_combo.addItem("Every 2 minutes", 120)
        self.interval_combo.addItem("Every 5 minutes", 300)
        self.interval_combo.addItem("Every 15 minutes", 900)

        cur_int = int(sync_cfg.get("auto_sync_interval_s", 60))
        idx = self.interval_combo.findData(cur_int)
        if idx != -1: self.interval_combo.setCurrentIndex(idx)
        int_row.addWidget(int_lbl)
        int_row.addWidget(self.interval_combo)
        int_row.addStretch()
        layout.addLayout(int_row)

        self.sync_cookies_cb = QCheckBox("Sync TikTok login session & cookies (authenticated across all devices)")
        self.sync_cookies_cb.setChecked(bool(sync_cfg.get("sync_cookies", True)))
        self.sync_cookies_cb.setStyleSheet("color: #e0e0e0; font-size: 8.5pt;")
        layout.addWidget(self.sync_cookies_cb)

        self.status_lbl = QLabel(getattr(self.sync_manager, 'last_sync_status', 'Not synced yet'))
        self.status_lbl.setStyleSheet("color: #8c96a8; font-size: 8pt; padding: 4px;")
        self.status_lbl.setWordWrap(True)
        layout.addWidget(self.status_lbl)

        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)
        self.sync_now_btn = QPushButton("Sync Now")
        self.sync_now_btn.clicked.connect(self._sync_now)

        save_btn = QPushButton("Save & Apply")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_and_close)

        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.sync_now_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Sync Directory", self.folder_edit.text() or os.path.expanduser("~"))
        if folder:
            self.folder_edit.setText(folder)

    def _get_current_method(self) -> str:
        if self.rb_webdav.isChecked(): return "webdav"
        if self.rb_rest.isChecked(): return "rest"
        return "folder"

    def _test_connection(self):
        method = self._get_current_method()
        self.status_lbl.setText("Testing connection...")
        self.status_lbl.setStyleSheet("color: #25F4EE; font-size: 8pt;")
        QApplication.processEvents()

        backend = None
        if method == "folder":
            backend = FolderSyncBackend(self.folder_edit.text().strip())
        elif method == "webdav":
            backend = WebDAVSyncBackend(
                server_url=self.webdav_url_edit.text().strip(),
                username=self.webdav_user_edit.text().strip(),
                password=self.webdav_pass_edit.text().strip()
            )
        elif method == "rest":
            backend = RestSyncBackend(
                endpoint_url=self.rest_url_edit.text().strip(),
                api_key=self.rest_key_edit.text().strip()
            )

        if backend:
            ok, msg = backend.test_connection()
            if ok:
                self.status_lbl.setText(f"✅ Success: {msg}")
                self.status_lbl.setStyleSheet("color: #00e676; font-size: 8pt;")
            else:
                self.status_lbl.setText(f"❌ Error: {msg}")
                self.status_lbl.setStyleSheet("color: #ff5252; font-size: 8pt;")

    def _sync_now(self):
        self._apply_to_settings()
        if self.sync_manager:
            self.sync_manager.reload_config()
            self.status_lbl.setText("Syncing now...")
            self.status_lbl.setStyleSheet("color: #25F4EE; font-size: 8pt;")
            QApplication.processEvents()
            ok, msg = self.sync_manager.sync_now()
            self.update_status(msg, is_error=not ok)

    def update_status(self, msg: str, is_error: bool = False):
        color = "#ff5252" if is_error else "#00e676"
        icon = "❌ " if is_error else "✅ "
        self.status_lbl.setText(icon + msg)
        self.status_lbl.setStyleSheet(f"color: {color}; font-size: 8pt;")

    def _apply_to_settings(self):
        sync_cfg = self.settings.setdefault("sync", {})
        sync_cfg["enabled"] = self.enable_cb.isChecked()
        sync_cfg["method"] = self._get_current_method()
        sync_cfg["folder_path"] = self.folder_edit.text().strip()
        sync_cfg["webdav_url"] = self.webdav_url_edit.text().strip()
        sync_cfg["webdav_username"] = self.webdav_user_edit.text().strip()
        sync_cfg["webdav_password"] = self.webdav_pass_edit.text().strip()
        sync_cfg["rest_url"] = self.rest_url_edit.text().strip()
        sync_cfg["rest_api_key"] = self.rest_key_edit.text().strip()
        sync_cfg["auto_sync_interval_s"] = self.interval_combo.currentData()
        sync_cfg["sync_cookies"] = self.sync_cookies_cb.isChecked()
        SettingsManager.save_settings(self.settings)

        if self.sync_cookies_cb.isChecked() and self.sync_manager:
            UniversalWebView.extract_all_cookies(lambda cks: cks and self.sync_manager.update_local_cookies(cks))

    def _save_and_close(self):
        self._apply_to_settings()
        if self.sync_manager:
            self.sync_manager.reload_config()
        self.accept()


class TikTokAutoLikerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"TikTok Live Auto Liker {APP_VERSION}")
        self.resize(1370, 800)

        # Resolve icon
        icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.favorites = SettingsManager.load_favorites()
        self.settings = SettingsManager.load_settings()
        self.active_streams = {}
        self.fav_widgets = {}
        self.avatar_pixmap_cache = {}
        self.sort_key = 'live'
        self.sort_reverse = True
        self.sort_buttons = {}
        self.avatar_manager = QNetworkAccessManager(self)

        self.is_monitoring = False
        self.is_logged_in = False
        self.login_webview = None
        self.waiting_webview = None
        self.explore_webview = None
        self._has_handled_login = False

        self.sync_mgr = SyncManager(data_dir=DATA_DIR, parent=self)
        self.sync_mgr.sync_completed.connect(self._on_sync_completed)
        self.sync_mgr.sync_failed.connect(self._on_sync_failed)
        self.sync_mgr.cookies_updated.connect(self._on_cookies_received)
        self._sync_dialog = None
        self.stats_mgr = StatsManager(data_dir=DATA_DIR)

        # Restore saved cookies if present
        saved_cookies, _ = self.sync_mgr._read_cookies()
        if saved_cookies:
            UniversalWebView.inject_cookies_into_profile(saved_cookies, USER_DATA_DIR)

        self._apply_stylesheet()
        self._setup_ui()
        self._setup_webview_engine()
        QTimer.singleShot(2000, self._initial_sync)
        QTimer.singleShot(3000, self.check_for_updates)

    def _on_cookies_received(self, cookies):
        if cookies:
            UniversalWebView.inject_cookies_into_profile(cookies, USER_DATA_DIR)

    def _on_cookies_extracted(self, cookies):
        if cookies and hasattr(self, 'sync_mgr'):
            self.sync_mgr.update_local_cookies(cookies)

    def _open_kofi(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/K3K314GUP?ref=tiktok_live_auto_liker_app"))

    def _add_user_list_item(self, username):
        item = QListWidgetItem(self.fav_list)
        item.setData(Qt.ItemDataRole.UserRole, username)

        is_enabled = self.favorites.get(username, True)
        is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
        widget = UserListItem(username, is_enabled, is_muted)
        widget.toggle_btn.clicked.connect(lambda _, un=username: QTimer.singleShot(0, lambda: self.toggle_tapper(un)))
        widget.mute_btn.clicked.connect(lambda _, un=username: QTimer.singleShot(0, lambda: self.toggle_mute(un)))
        widget.del_btn.clicked.connect(lambda _, un=username: QTimer.singleShot(0, lambda: self.remove_favorite(un)))

        if username in self.avatar_pixmap_cache:
            widget.set_avatar(self.avatar_pixmap_cache[username])
            widget.has_avatar = True
        else:
            avatar_path = os.path.join(AVATARS_DIR, f"{username}.png")
            if os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
                self.avatar_pixmap_cache[username] = pixmap
                widget.set_avatar(pixmap)
                widget.has_avatar = True

        item.setSizeHint(widget.sizeHint())
        self.fav_list.setItemWidget(item, widget)
        self.fav_widgets[username] = widget

    def _on_user_clicked(self, item):
        username = item.data(Qt.ItemDataRole.UserRole)
        if username not in self.active_streams:
            self.status_label.setText(f"● Opening stream manually: @{username}")
            tapper_enabled = self.favorites.get(username, True)
            is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
            tab = LiveTab(username, self.settings, tapper_enabled, is_muted, stats_mgr=self.stats_mgr, tabs_widget=self.tabs)
            tab.stream_ended.connect(self._on_stream_ended_in_tab)

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
            if hasattr(self, 'sync_mgr'):
                self.sync_mgr.record_local_change()

            if username in self.active_streams:
                self.active_streams[username].set_tapper_enabled(new_state)
                tab_idx = self.tabs.indexOf(self.active_streams[username])
                if tab_idx != -1:
                    prefix = "❤️ " if new_state else ""
                    self.tabs.setTabText(tab_idx, f"{prefix}LIVE: @{username}")
            elif new_state and username in getattr(self, 'known_live', set()):
                is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
                tab = LiveTab(username, self.settings, tapper_enabled=True, is_muted=is_muted, stats_mgr=self.stats_mgr, tabs_widget=self.tabs)
                tab.stream_ended.connect(self._on_stream_ended_in_tab)
                idx = self.tabs.addTab(tab, f"❤️ LIVE: @{username}")
                self.tabs.setCurrentIndex(idx)
                self.active_streams[username] = tab
                self._update_waiting_tab()

            if getattr(self, '_pending_checks', 0) == 0:
                self._update_status_label()
            self._sort_list()

    def _download_avatar(self, username, url):
        if not url:
            return
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
                pixmap.save(os.path.join(AVATARS_DIR, f"{username}.png"))
                self.avatar_pixmap_cache[username] = pixmap
                if username in self.fav_widgets:
                    self.fav_widgets[username].set_avatar(pixmap)
                    self.fav_widgets[username].has_avatar = True
        reply.deleteLater()

    def _remove_tab_close_button(self, idx):
        bar = self.tabs.tabBar()
        for pos in (bar.ButtonPosition.LeftSide, bar.ButtonPosition.RightSide):
            bar.setTabButton(idx, pos, None)

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#left_panel {
                background-color: #121212;
            }
            QWidget {
                color: #E0E0E0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
            QTabWidget::tab-bar {
                alignment: left;
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
            if hasattr(self, 'check_timer') and self.check_timer.isActive():
                self.check_timer.stop()

            if getattr(self, 'checker', None):
                self.checker.cleanup()

            for tab in list(self.active_streams.values()):
                tab.cleanup()
            self.active_streams.clear()

            if getattr(self, 'explore_webview', None):
                self.explore_webview.cleanup()
                self.explore_webview.deleteLater()
            if getattr(self, 'waiting_webview', None):
                self.waiting_webview.cleanup()
                self.waiting_webview.deleteLater()
            if getattr(self, 'sync_mgr', None):
                self.sync_mgr.stop()
            if getattr(self, 'login_webview', None):
                self.login_webview.cleanup()
                self.login_webview.deleteLater()
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

        # Favorites container
        fav_container = QWidget()
        fav_container_layout = QVBoxLayout(fav_container)
        fav_container_layout.setContentsMargins(0, 0, 0, 0)
        fav_container_layout.setSpacing(5)

        fav_header = QHBoxLayout()
        fav_header.setContentsMargins(12, 0, 4, 0)
        fav_title_lbl = QLabel("Favorites")
        fav_title_lbl.setStyleSheet(
            "color: #FE2C55; font-weight: bold; font-size: 15px; background: transparent; border: none;"
        )
        fav_header.addWidget(fav_title_lbl)
        fav_header.addStretch()
        fav_container_layout.addLayout(fav_header)

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
        self.search_input.returnPressed.connect(self.add_favorite)
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
            ('tapper', '\u2764\uFE0F Tapper'),
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
        self._sort_list()
        self._update_sort_buttons()
        fav_layout.addWidget(self.fav_list)

        fav_container_layout.addWidget(fav_box)
        left_layout.addWidget(fav_container, 1)

        # Settings container
        settings_container = QWidget()
        settings_container_layout = QVBoxLayout(settings_container)
        settings_container_layout.setContentsMargins(0, 0, 0, 0)
        settings_container_layout.setSpacing(5)

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

        # --- Data Management ---
        data_container = QWidget()
        data_layout = QGridLayout(data_container)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(6)

        btn_style = """
            QPushButton {
                background-color: #2a2a2a;
                color: #8c96a8;
                border: 1px solid #364057;
                border-radius: 5px;
                padding: 5px 8px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #364057;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """

        self.backup_btn = QPushButton("💾 Backup")
        self.backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.backup_btn.setStyleSheet(btn_style)
        self.backup_btn.clicked.connect(self.backup_data)

        self.restore_btn = QPushButton("📂 Restore")
        self.restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restore_btn.setStyleSheet(btn_style)
        self.restore_btn.clicked.connect(self.restore_data)

        self.cloud_sync_btn = QPushButton("☁️ Cloud Sync")
        self.cloud_sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cloud_sync_btn.setStyleSheet(btn_style)
        self.cloud_sync_btn.clicked.connect(self.open_sync_dialog)

        self.analytics_btn = QPushButton("📊 Analytics & Stats")
        self.analytics_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analytics_btn.setStyleSheet(btn_style)
        self.analytics_btn.clicked.connect(self.open_analytics_dialog)

        data_layout.addWidget(self.backup_btn, 0, 0)
        data_layout.addWidget(self.restore_btn, 0, 1)
        data_layout.addWidget(self.cloud_sync_btn, 1, 0)
        data_layout.addWidget(self.analytics_btn, 1, 1)
        left_layout.addWidget(data_container)

        # Update Banner
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

        self.sync_status_lbl = QLabel("☁️ Sync: Off")
        self.sync_status_lbl.setObjectName("sync_status_lbl")
        self.sync_status_lbl.setStyleSheet("color: #777; font-size: 8pt; margin-top: -2px; padding: 2px 4px; border-radius: 4px;")
        self.sync_status_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_status_lbl.setToolTip("Click to open Cloud Sync settings")
        self.sync_status_lbl.mousePressEvent = lambda e: self.open_sync_dialog()
        left_layout.addWidget(self.sync_status_lbl)

        splitter.addWidget(left_panel)

        self.tabs = QTabWidget()
        self.tab_bar = PulsingTabBar(self.tabs)
        self.tabs.setTabBar(self.tab_bar)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_bar.setExpanding(False)
        self.tabs.currentChanged.connect(self._on_tab_changed)

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

        debug_btn = QPushButton("Debug")
        debug_btn.setToolTip("Open Developer Tools for Active Tab")
        debug_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        debug_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 8.5pt;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        debug_btn.clicked.connect(self.open_debug_console)

        corner_layout.addWidget(debug_btn)
        corner_layout.addWidget(refresh_btn)
        corner_layout.addWidget(self.signout_btn)
        self.tabs.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

        splitter.addWidget(self.tabs)
        splitter.setSizes([350, 850])

    def _setup_webview_engine(self):
        self.waiting_webview = UniversalWebView(
            parent=self,
            user_data_folder=USER_DATA_DIR
        )
        self.waiting_webview.load_html(WAITING_HTML)
        self.tab_bar.waiting_tab = self.waiting_webview
        self.status_label.setText("● Checking login status...")
        self._update_waiting_tab()
        QTimer.singleShot(1200, self._start_auth_flow)

    def _start_auth_flow(self):
        self.login_webview = UniversalWebView(
            parent=self,
            url="https://www.tiktok.com/login",
            user_data_folder=USER_DATA_DIR
        )
        self.login_webview.set_muted(True)
        self.login_webview.source_changed.connect(self._on_login_source_changed)
        QTimer.singleShot(4500, self._reveal_login_tab)

    def _on_login_source_changed(self, url_str):
        if not url_str:
            return
        lower = url_str.lower()
        # Do not prematurely treat QR code / passport / auth subpages as login success
        is_auth_subpage = any(x in lower for x in [
            "login", "passport", "auth", "qrcode", "verify", "checkpoint"
        ])
        if not is_auth_subpage and "tiktok.com" in lower:
            QMetaObject.invokeMethod(self, "_on_login_success", Qt.ConnectionType.QueuedConnection)

    def _handle_explore_url(self, url):
        if "tiktok.com/@" in url and "/live" in url:
            try:
                username = url.split("tiktok.com/@")[1].split("/")[0].split("?")[0]
                if username and username not in self.favorites:
                    self.search_input.setText(username)
            except Exception:
                pass

    def _update_waiting_tab(self):
        if not hasattr(self, 'waiting_webview') or not self.waiting_webview:
            return

        idx = self.tabs.indexOf(self.waiting_webview)

        is_login_visible = False
        if getattr(self, 'login_webview', None) is not None:
            is_login_visible = self.tabs.indexOf(self.login_webview) != -1

        needs_waiting = len(self.active_streams) == 0 and not is_login_visible

        if needs_waiting and idx == -1:
            new_idx = self.tabs.addTab(self.waiting_webview, "")
            self._remove_tab_close_button(new_idx)
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

        self.tabs.blockSignals(True)
        try:
            # 1. First remove and cleanup login tab
            if self.login_webview is not None:
                idx = self.tabs.indexOf(self.login_webview)
                if idx != -1:
                    self.tabs.removeTab(idx)
                self.login_webview.cleanup()
                self.login_webview.deleteLater()
                self.login_webview = None

            # 2. Setup Explore tab at index 0
            if self.explore_webview is None:
                self.explore_webview = UniversalWebView(
                    parent=self,
                    user_data_folder=USER_DATA_DIR,
                    lazyload=True
                )
                self.explore_webview.set_muted(True)
                self.explore_webview.source_changed.connect(self._handle_explore_url)
                self._explore_loaded = False
                self.tabs.insertTab(0, self.explore_webview, "Explore TikTok")
                self._remove_tab_close_button(0)

            # 3. Ensure waiting tab is added now that login tab is gone
            self._update_waiting_tab()
        finally:
            self.tabs.blockSignals(False)

        self._fallback_tab_selection()
        self._start_monitoring()
        UniversalWebView.extract_all_cookies(self._on_cookies_extracted)

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
            self._remove_tab_close_button(idx)
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

    def open_debug_console(self):
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'webview') and hasattr(current_widget.webview, 'open_dev_tools'):
            current_widget.webview.open_dev_tools()
        elif hasattr(current_widget, 'open_dev_tools'):
            current_widget.open_dev_tools()

    def sign_out(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Sign Out of TikTok")
        msg_box.setText("Are you sure you want to sign out of TikTok?")
        msg_box.setInformativeText("This will close active streams and clear the session.")
        msg_box.setIcon(QMessageBox.Icon.Question)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1e28;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #252c3c;
                color: #ffffff;
                border: 1px solid #364057;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 65px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2f384d;
            }
        """)

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
        if hasattr(self, 'sync_mgr'):
            self.sync_mgr.clear_local_cookies()

        # Stop monitoring and clean up checker
        if hasattr(self, 'check_timer') and self.check_timer.isActive():
            self.check_timer.stop()
        if getattr(self, 'checker', None):
            self.checker.cleanup()
            self.checker = None
        self.is_monitoring = False

        # Close all active stream tabs
        for username, tab in list(self.active_streams.items()):
            tab_idx = self.tabs.indexOf(tab)
            if tab_idx != -1:
                self.tabs.removeTab(tab_idx)
            tab.cleanup()
            tab.deleteLater()
        self.active_streams.clear()

        if hasattr(self, 'known_live'):
            self.known_live.clear()
        if hasattr(self, 'consecutive_offline'):
            self.consecutive_offline.clear()
        self._pending_checks = 0
        self._completed_checks = 0

        for widget in self.fav_widgets.values():
            widget.set_status(False)

        if getattr(self, 'explore_webview', None) is not None:
            idx = self.tabs.indexOf(self.explore_webview)
            if idx != -1:
                self.tabs.removeTab(idx)
            self.explore_webview.cleanup()
            self.explore_webview.deleteLater()
            self.explore_webview = None
            self._explore_loaded = False

        if getattr(self, 'login_webview', None) is not None:
            idx = self.tabs.indexOf(self.login_webview)
            if idx != -1:
                self.tabs.removeTab(idx)
            self.login_webview.cleanup()
            self.login_webview.deleteLater()
            self.login_webview = None

        if getattr(self, 'waiting_webview', None) is not None:
            idx = self.tabs.indexOf(self.waiting_webview)
            if idx != -1:
                self.tabs.removeTab(idx)

        self.status_label.setText("● Signing out...")
        self.login_webview = UniversalWebView(
            parent=self,
            url="https://www.tiktok.com/logout",
            user_data_folder=USER_DATA_DIR
        )
        self.login_webview.source_changed.connect(self._on_login_source_changed)

        QTimer.singleShot(3000, lambda: getattr(self, 'login_webview', None) and self.login_webview.load_url("https://www.tiktok.com/login"))
        QTimer.singleShot(3500, self._reveal_login_tab)

    def add_favorite(self):
        username = self.search_input.text().strip().replace("@", "")
        if not username:
            return
        if username not in self.favorites:
            self.favorites[username] = True
            self._add_user_list_item(username)
            self._sort_list()
            SettingsManager.save_favorites(self.favorites)
            if hasattr(self, 'sync_mgr'):
                self.sync_mgr.record_local_change()
            self.search_input.clear()
            self.status_label.setText(f"● Added {username} to favorites.")
            if self.is_monitoring:
                self.checker.check_users([username])
        else:
            QMessageBox.information(self, "Info", "User is already in favorites.")

    def remove_favorite(self, username=None):
        if username is None:
            return

        if username in self.active_streams:
            tab_idx = self.tabs.indexOf(self.active_streams[username])
            if tab_idx != -1:
                self.tabs.removeTab(tab_idx)
            self.active_streams[username].cleanup()
            self.active_streams[username].deleteLater()
            del self.active_streams[username]
            self._update_waiting_tab()
            self._fallback_tab_selection()

        if hasattr(self, 'known_live'):
            self.known_live.discard(username)

        if username in self.favorites:
            if isinstance(self.favorites, list):
                self.favorites.remove(username)
            elif isinstance(self.favorites, dict):
                del self.favorites[username]

        self.fav_widgets.pop(username, None)
        self._sort_list()
        SettingsManager.save_favorites(self.favorites)
        if hasattr(self, 'sync_mgr'):
            self.sync_mgr.record_deletion(username)
        self.status_label.setText(f"● Removed {username} from favorites.")

        if getattr(self, 'is_monitoring', False) and hasattr(self, 'checker') and self.checker:
            self.checker.queue = [u for u in self.checker.queue if u != username]

    def save_settings_ui(self):
        self.settings["like_delay_ms"] = self.delay_slider.value()
        self.settings["randomization_ms"] = self.rand_slider.value()
        self.settings["updated_at"] = time.time()
        SettingsManager.save_settings(self.settings)

        for stream in self.active_streams.values():
            stream.update_settings(self.settings)
        if hasattr(self, 'sync_mgr'):
            self.sync_mgr.record_local_change()

    def reset_settings_to_default(self):
        self.delay_slider.setValue(50)
        self.rand_slider.setValue(50)

    def backup_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Backup", "", "Zip Files (*.zip)")
        if file_path:
            if not file_path.lower().endswith(".zip"):
                file_path += ".zip"
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                if os.path.exists(SETTINGS_FILE):
                    shutil.copy2(SETTINGS_FILE, temp_dir)
                if os.path.exists(FAVORITES_FILE):
                    shutil.copy2(FAVORITES_FILE, temp_dir)
                if os.path.exists(AVATARS_DIR):
                    shutil.copytree(AVATARS_DIR, os.path.join(temp_dir, "avatars"))

                base_name = file_path[:-4]
                shutil.make_archive(base_name, 'zip', temp_dir)

            QMessageBox.information(self, "Backup Successful", f"Data backed up to {file_path}")

    def restore_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup", "", "Zip Files (*.zip)")
        if file_path:
            reply = QMessageBox.question(self, "Restore Data", "This will overwrite your current favorites and settings. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    shutil.unpack_archive(file_path, temp_dir)

                    src_settings = os.path.join(temp_dir, os.path.basename(SETTINGS_FILE))
                    if os.path.exists(src_settings):
                        shutil.copy2(src_settings, SETTINGS_FILE)
                    src_favs = os.path.join(temp_dir, os.path.basename(FAVORITES_FILE))
                    if os.path.exists(src_favs):
                        shutil.copy2(src_favs, FAVORITES_FILE)
                    if os.path.exists(os.path.join(temp_dir, "avatars")):
                        if os.path.exists(AVATARS_DIR):
                            shutil.rmtree(AVATARS_DIR)
                        shutil.copytree(os.path.join(temp_dir, "avatars"), AVATARS_DIR)

                # Dynamically reload UI without requiring app restart
                self.favorites = SettingsManager.load_favorites()
                self.settings = SettingsManager.load_settings()
                self.avatar_pixmap_cache.clear()
                self.fav_list.clear()
                self.fav_widgets.clear()
                for fav in self.favorites:
                    self._add_user_list_item(fav)
                self._sort_list()
                self.delay_slider.setValue(self.settings.get("like_delay_ms", 100))
                self.rand_slider.setValue(self.settings.get("randomization_ms", 50))
                self._update_status_label()
                if hasattr(self, 'sync_mgr'):
                    self.sync_mgr.record_local_change()
                QMessageBox.information(self, "Restore Successful", "Data restored successfully!")

    def open_sync_dialog(self):
        if not hasattr(self, '_sync_dialog') or not self._sync_dialog:
            self._sync_dialog = SyncSettingsDialog(self, sync_manager=self.sync_mgr, settings=self.settings)
        self._sync_dialog.show()
        self._sync_dialog.raise_()
        self._sync_dialog.activateWindow()

    def open_analytics_dialog(self):
        dlg = AnalyticsDialog(self.stats_mgr, parent=self)
        dlg.exec()

    def _initial_sync(self):
        if hasattr(self, 'sync_mgr') and self.sync_mgr.backend:
            self.sync_status_lbl.setText("☁️ Syncing...")
            self.sync_mgr.sync_now_async()

    def _on_sync_completed(self, msg, has_local_changes):
        short_msg = (msg[:35] + "...") if len(msg) > 35 else msg
        self.sync_status_lbl.setText("☁️ " + short_msg)
        if hasattr(self, '_sync_dialog') and self._sync_dialog and self._sync_dialog.isVisible():
            self._sync_dialog.update_status(msg, is_error=False)

        if has_local_changes:
            self.favorites = SettingsManager.load_favorites()
            self.settings = SettingsManager.load_settings()

            self.delay_slider.blockSignals(True)
            self.rand_slider.blockSignals(True)
            self.delay_slider.setValue(self.settings.get("like_delay_ms", 100))
            self.rand_slider.setValue(self.settings.get("randomization_ms", 50))
            self.delay_val_lbl.setText(f"{self.delay_slider.value()} ms")
            self.rand_val_lbl.setText(f"{self.rand_slider.value()} ms")
            self.delay_slider.blockSignals(False)
            self.rand_slider.blockSignals(False)

            for stream in self.active_streams.values():
                stream.update_settings(self.settings)

            current_fav_users = set(self.favorites.keys())
            existing_widget_users = set(self.fav_widgets.keys())

            for un in current_fav_users - existing_widget_users:
                self._add_user_list_item(un)

            for un in existing_widget_users - current_fav_users:
                for i in range(self.fav_list.count()):
                    item = self.fav_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == un:
                        self.fav_list.takeItem(i)
                        break
                self.fav_widgets.pop(un, None)
                if hasattr(self, 'checker') and hasattr(self.checker, 'queue'):
                    self.checker.queue = [u for u in self.checker.queue if u != un]

            for un in current_fav_users & existing_widget_users:
                state = self.favorites.get(un, True)
                if isinstance(state, dict):
                    state = state.get("tapper_enabled", True)
                self.fav_widgets[un].set_tapper_enabled(state)
                if un in self.active_streams:
                    self.active_streams[un].set_tapper_enabled(state)

            self._sort_list()
            self._update_status_label()

    def _on_sync_failed(self, err_msg):
        self.sync_status_lbl.setText("☁️ Sync error")
        if hasattr(self, '_sync_dialog') and self._sync_dialog and self._sync_dialog.isVisible():
            self._sync_dialog.update_status(err_msg, is_error=True)

    def check_for_updates(self, manual=False):
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
        self._completed_checks = 0
        self.status_label.setText(f"● Checking live status... (0/{self._pending_checks})")
        self.checker.check_users(users)

    def _update_status_label(self):
        total = len(self.favorites)
        live_count = len(getattr(self, 'known_live', set()))
        liking_count = sum(1 for t in self.active_streams.values() if getattr(t, 'tapper_enabled', False))
        self.status_label.setText(f"● Monitoring {total} users │ {live_count} live │ {liking_count} liking")

    # --- Sort constants ---
    _SORT_DEFAULT_REVERSE = {
        'name':   False,
        'live':   True,
        'tapper': True,
        'mute':   False,
    }

    def _on_sort_clicked(self, key):
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = self._SORT_DEFAULT_REVERSE[key]
        self._update_sort_buttons()
        self._sort_list()

    def _update_sort_buttons(self):
        labels = {
            'name':   'Name',
            'live':   '\U0001f4e1 Live',
            'tapper': '\u2764\uFE0F Tapper',
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
        if not hasattr(self, 'sort_key') or not hasattr(self, 'fav_list'):
            return
        if getattr(self, '_rebuilding_sort', False):
            return
        count = self.fav_list.count()
        if count == 0:
            return

        usernames = [
            self.fav_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(count)
        ]

        filtered_usernames = [u for u in usernames if u in self.favorites]

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

        sorted_usernames = sorted(filtered_usernames, key=sort_key_fn, reverse=reverse)
        if sorted_usernames == usernames:
            return

        self._rebuilding_sort = True
        try:
            self.fav_list.clear()
            self.fav_widgets.clear()
            for un in sorted_usernames:
                self._add_user_list_item(un)
            for un in sorted_usernames:
                if un in self.fav_widgets:
                    self.fav_widgets[un].set_status(un in known_live)
        finally:
            self._rebuilding_sort = False

    def on_live_status(self, username, is_live, avatar_url="", is_error=False):
        # Progress counter must ALWAYS increment, even if username was deleted mid-scan
        total = getattr(self, '_pending_checks', 0)
        if total > 0:
            self._completed_checks = getattr(self, '_completed_checks', 0) + 1
            completed = self._completed_checks
            self.status_label.setText(f"● Checking live status... ({completed}/{total})")

        # When all results are in, reset counter and update summary
        if total > 0 and getattr(self, '_completed_checks', 0) >= total:
            self._pending_checks = 0
            self._completed_checks = 0
            self._update_status_label()

        if username not in self.favorites:
            return

        if is_error:
            if username in self.fav_widgets and username not in getattr(self, 'known_live', set()):
                self.fav_widgets[username].set_status(False)
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

            self._sort_list()
            tapper_enabled = self.favorites.get(username, True)
            if username not in self.active_streams and tapper_enabled:
                is_muted = self.settings.setdefault("muted_users", {}).get(username, True)
                tab = LiveTab(username, self.settings, tapper_enabled, is_muted, stats_mgr=self.stats_mgr, tabs_widget=self.tabs)
                tab.stream_ended.connect(self._on_stream_ended_in_tab)

                prefix = "❤️ " if tapper_enabled else ""
                idx = self.tabs.addTab(tab, f"{prefix}LIVE: @{username}")
                self.tabs.setCurrentIndex(idx)

                self.active_streams[username] = tab
                self._update_waiting_tab()
        else:
            if avatar_url and username in self.fav_widgets:
                if not self.fav_widgets[username].has_avatar and getattr(self.fav_widgets[username], 'current_avatar_url', None) != avatar_url:
                    self.fav_widgets[username].current_avatar_url = avatar_url
                    self._download_avatar(username, avatar_url)

            self.consecutive_offline[username] = self.consecutive_offline.get(username, 0) + 1

            # Require 2 consecutive clean offline checks only if creator was actively streaming or known live
            if username in self.known_live or username in self.active_streams:
                if self.consecutive_offline[username] >= 2:
                    self.known_live.discard(username)
                    if username in self.fav_widgets:
                        self.fav_widgets[username].set_status(False)
                    self._sort_list()

                    if username in self.active_streams:
                        tab_idx = self.tabs.indexOf(self.active_streams[username])
                        if tab_idx != -1:
                            self.tabs.removeTab(tab_idx)
                        self.active_streams[username].cleanup()
                        self.active_streams[username].deleteLater()
                        del self.active_streams[username]
                        self._update_waiting_tab()
                        self._fallback_tab_selection()
            else:
                # If creator was not live, immediately update UI from "Checking..." to "Offline"
                if username in self.fav_widgets:
                    self.fav_widgets[username].set_status(False)
                self._sort_list()

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
        if hasattr(widget, 'cleanup'):
            widget.cleanup()
        widget.deleteLater()
        self._update_waiting_tab()
        self._fallback_tab_selection()

    def _fallback_tab_selection(self):
        current = self.tabs.currentWidget()

        # Already on a live stream — nothing to do.
        if isinstance(current, LiveTab):
            return

        # Already on the idle tab — nothing to do.
        if current == self.waiting_webview:
            return

        # If there are live streams, prefer the first one.
        if self.active_streams:
            first_tab = next(iter(self.active_streams.values()))
            idx = self.tabs.indexOf(first_tab)
            if idx != -1:
                self.tabs.setCurrentIndex(idx)
                return

        # No live streams — always land on the System Idle tab (never the Explore tab).
        # This prevents explore_webview from auto-loading and autoplaying when the last
        # streamer goes offline.
        if self.waiting_webview:
            idx = self.tabs.indexOf(self.waiting_webview)
            if idx != -1:
                self.tabs.setCurrentIndex(idx)
                return

    def _on_tab_changed(self, index):
        if index < 0:
            return
        current_widget = self.tabs.widget(index)
        if current_widget is None:
            return

        is_explore = (self.explore_webview is not None and current_widget == self.explore_webview)

        if is_explore:
            # Guard: if there are no active streams and the waiting tab is present, this is a
            # transient state caused by Qt's automatic tab selection during removeTab().
            # _fallback_tab_selection() will redirect to the idle tab momentarily —
            # don't load or unmute the explore tab now to avoid autoplay / audio leaks.
            waiting_in_bar = (
                getattr(self, 'waiting_webview', None) is not None
                and self.tabs.indexOf(self.waiting_webview) != -1
            )
            if not self.active_streams and waiting_in_bar:
                return

            if not getattr(self, '_explore_loaded', False):
                self._explore_loaded = True
                self.explore_webview.load_url("https://www.tiktok.com/")
            self.explore_webview.set_muted(False)
            self.explore_webview.set_background_mode(False)
        else:
            if self.explore_webview is not None and getattr(self, '_explore_loaded', False):
                self.explore_webview.set_muted(True)
                self.explore_webview.set_background_mode(True)

        for username, tab in self.active_streams.items():
            tab.set_background_mode(tab != current_widget)

    def _on_stream_ended_in_tab(self, username, reason):
        if username not in self.active_streams:
            return

        self.status_label.setText(f"● Stream ended for @{username} ({reason})")

        if hasattr(self, 'known_live'):
            self.known_live.discard(username)
        if username in self.fav_widgets:
            self.fav_widgets[username].set_status(False)
        self._sort_list()

        tab = self.active_streams[username]
        tab_idx = self.tabs.indexOf(tab)
        if tab_idx != -1:
            self.tabs.removeTab(tab_idx)
        tab.cleanup()
        tab.deleteLater()
        del self.active_streams[username]
        self._update_waiting_tab()
        self._fallback_tab_selection()


if __name__ == "__main__":
    if "--headless" in sys.argv or "--sync-only" in sys.argv:
        from headless_runner import main as headless_main
        headless_main()
        sys.exit(0)

    app = QApplication(sys.argv)
    qInstallMessageHandler(_qt_message_handler)

    # Cross-platform font setup
    if sys.platform == "darwin":
        app.setFont(QFont(".AppleSystemUIFont", 10))
    elif sys.platform == "win32":
        app.setFont(QFont("Segoe UI", 10))
    else:
        app.setFont(QFont("sans-serif", 10))

    window = TikTokAutoLikerApp()
    window.show()
    sys.exit(app.exec())
