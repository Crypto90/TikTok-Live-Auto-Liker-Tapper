#!/usr/bin/env python3
"""Headless Linux Server Runner for TikTok Live Auto-Liker / Tapper.

Runs 24/7 on servers or VPS instances without a desktop display.
Features:
- Continuous multi-device synchronization (Favorites, Settings, Toggles).
- Headless stream monitoring & native in-page auto-tapping.
- Built-in Web Dashboard on port 8080 (http://server-ip:8080).
- Automatic virtual display detection (Xvfb) for headless Linux.

Usage:
    python headless_runner.py [--port 8080] [--no-web] [--sync-only]
"""

import os
import sys
import time
import json
import signal
import shutil
import argparse
import subprocess
from typing import Dict, Any, List

# Suppress console spam from QtWebEngine
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --log-level=3 --disable-gpu-memory-buffer-video-frames"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"


def ensure_virtual_display_on_linux():
    """Detect if running on headless Linux without a display and launch Xvfb if available."""
    if sys.platform.startswith("linux"):
        display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        if not display:
            # Check if Xvfb is available
            xvfb_path = shutil.which("Xvfb")
            if xvfb_path:
                display_num = ":99"
                print(f"[Display] No DISPLAY set. Starting in-memory virtual X11 server on {display_num} via Xvfb...")
                try:
                    proc = subprocess.Popen([xvfb_path, display_num, "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.environ["DISPLAY"] = display_num
                    time.sleep(1.0)
                    print(f"[Display] Virtual X11 display active on {display_num}")
                    return proc
                except Exception as e:
                    print(f"[Display] Warning: Failed to spawn Xvfb automatically: {e}")
            else:
                print("=" * 70)
                print("  [WARNING] No active X11 / Wayland display detected!")
                print("  To run headless on Linux servers without a GUI desktop, please run:")
                print("    xvfb-run -a python headless_runner.py")
                print("  Or install Xvfb:")
                print("    sudo apt-get install -y xvfb")
                print("=" * 70)
    return None


# Check and configure display before importing PyQt6
xvfb_proc = ensure_virtual_display_on_linux()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QObject, pyqtSlot

from webview_engine import UniversalWebView
from sync_manager import SyncManager, get_device_name
from web_server import HeadlessWebServer
from stats_manager import StatsManager


def get_server_data_dir() -> str:
    if os.path.exists("favorites.json") or os.path.exists("settings.json"):
        return os.path.abspath(".")
    base = os.path.expanduser("~/.config/tiktok_live_auto_liker")
    os.makedirs(base, exist_ok=True)
    return base


DATA_DIR = get_server_data_dir()
USER_DATA_DIR = os.path.join(DATA_DIR, "userdata")
os.makedirs(USER_DATA_DIR, exist_ok=True)


class HeadlessStreamTab(QObject):
    """Headless tapping session for an active live streamer."""
    def __init__(self, username: str, settings: dict, tapper_enabled: bool = True, stats_mgr=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.settings = settings
        self.tapper_enabled = tapper_enabled
        self.stats_mgr = stats_mgr
        self.session_id = None
        self.is_muted = True
        self.start_time = time.time()
        self.is_active = True
        self.verified_likes = 0
        self.taps_dispatched = 0
        self.room_likes = 0
        self.live_rate = 0.0
        self._last_verified = 0
        self._last_dispatched = 0
        self._last_stats_tick = time.time()

        self.webview = UniversalWebView(
            parent=None,
            url=f"https://www.tiktok.com/@{self.username}/live",
            user_data_folder=USER_DATA_DIR,
            is_headless=True
        )
        self.webview.set_muted(True)
        self.webview.navigation_completed.connect(self._on_nav_completed)

        # 1-second live stats polling timer
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._poll_stats)
        self._stats_timer.start(1000)

        # Health monitor timer (every 15 seconds)
        self._health_timer = QTimer(self)
        self._health_timer.timeout.connect(self._check_health)
        self._health_timer.start(15000)

    def _poll_stats(self):
        if self.is_active:
            self.webview.get_tapper_stats(self._on_tapper_stats_result)

    def _on_tapper_stats_result(self, result_dict):
        res = result_dict.get('result', {})
        if isinstance(res, str):
            try: res = json.loads(res)
            except Exception: res = {}
        if not isinstance(res, dict):
            return

        dispatched = int(res.get('dispatched', 0) or 0)
        verified = int(res.get('verified', 0) or 0)
        failed = int(res.get('failed', 0) or 0)
        room_likes = int(res.get('roomLikes', 0) or 0)

        now = time.time()
        dt = max(0.5, now - self._last_stats_tick)
        delta_v = max(0, verified - self._last_verified)
        delta_d = max(0, dispatched - self._last_dispatched)
        if delta_v > 0:
            self.live_rate = round(delta_v / dt, 1)
        elif delta_d > 0:
            self.live_rate = round(delta_d / dt, 1)
        else:
            self.live_rate = 0.0

        # Headless background catch-up watchdog:
        if self.tapper_enabled and dt >= 0.8:
            base = self.settings.get("like_delay_ms", 100)
            rand = self.settings.get("randomization_ms", 50)
            avg_delay_ms = max(40, base + (rand // 2))
            expected = int(round((dt * 1000.0) / avg_delay_ms))
            needed = max(0, expected - delta_d)
            if needed > 0:
                self.webview.burst_tapper(needed)

        self._last_stats_tick = now
        self._last_verified = verified
        self._last_dispatched = dispatched
        self.verified_likes = verified
        self.taps_dispatched = dispatched
        self.room_likes = room_likes

        if self.stats_mgr and self.session_id:
            self.stats_mgr.record_progress(self.session_id, verified, dispatched, failed, room_likes)

    def _on_nav_completed(self, success, url):
        if success:
            self.webview.set_muted(True)
            self.webview.evaluate_js("(function() { var v = document.querySelector('video'); if (v && v.paused) v.play().catch(function(){}); })();")
            base = self.settings.get("like_delay_ms", 100)
            rand = self.settings.get("randomization_ms", 50)
            self.webview.inject_in_page_tapper(base, rand, enabled=self.tapper_enabled)

            if self.stats_mgr and not self.session_id:
                self.session_id = self.stats_mgr.start_session(self.username)

    def set_tapper_enabled(self, enabled: bool):
        self.tapper_enabled = enabled
        self.webview.set_tapper_enabled(enabled)

    def update_settings(self, settings: dict):
        self.settings = settings
        base = self.settings.get("like_delay_ms", 100)
        rand = self.settings.get("randomization_ms", 50)
        self.webview.set_tapper_rate(base, rand)

    def _check_health(self):
        js = """(function() {
            var v = document.querySelector('video');
            var bodyText = document.body ? document.body.innerText : '';
            var ended = /live.has.ended|stream.ended|broadcast.ended|replay/i.test(bodyText);
            return { has_video: !!v, ended: ended, url: window.location.href };
        })();"""
        self.webview.evaluate_js(js, self._on_health_result)

    def _on_health_result(self, result_dict):
        res = result_dict.get('result', {})
        if isinstance(res, str):
            try: res = json.loads(res)
            except Exception: res = {}
        if isinstance(res, dict):
            if res.get("ended", False):
                self.is_active = False

    def cleanup(self):
        self._health_timer.stop()
        if hasattr(self, '_stats_timer'):
            self._stats_timer.stop()
        if self.stats_mgr and self.session_id:
            self.stats_mgr.end_session(self.session_id, reason="ended")
            self.session_id = None
        self.webview.stop_tapper()
        self.webview.cleanup()
        self.webview.deleteLater()


class HeadlessServerManager(QObject):
    """Main orchestrator for headless live checking, tapping, sync, and web interface."""
    def __init__(self, port: int = 8080, enable_web: bool = True):
        super().__init__()
        self.port = port
        self.enable_web = enable_web
        self.start_time = time.time()
        self.logs: List[dict] = []

        # 1. Sync Manager
        self.sync_mgr = SyncManager(data_dir=DATA_DIR, parent=self)
        self.sync_mgr.sync_completed.connect(self._on_sync_completed)
        self.sync_mgr.sync_failed.connect(self._on_sync_failed)
        self.sync_mgr.cookies_updated.connect(self._on_cookies_updated)
        self.stats_mgr = StatsManager(data_dir=DATA_DIR)

        # Restore saved cookies if present
        saved_cookies, _ = self.sync_mgr._read_cookies()
        if saved_cookies:
            UniversalWebView.inject_cookies_into_profile(saved_cookies, USER_DATA_DIR)
            self.log(f"[AUTH] Injected {len(saved_cookies)} saved TikTok cookies into browser profile.")

        # 2. Local State
        self.favorites: Dict[str, Any] = self._load_favorites()
        self.settings: dict = self._load_settings()
        self.known_live: set = set()
        self.active_streams: Dict[str, HeadlessStreamTab] = {}
        self.avatars: Dict[str, str] = {}

        # 3. Checkers
        self.workers = []
        self.idle_workers = []
        self.check_queue = []

        # 4. Web Dashboard
        self.web_server = None
        if self.enable_web:
            self.web_server = HeadlessWebServer(host="0.0.0.0", port=self.port, runner_ref=self)
            self.web_server.start()

        # 5. Monitoring loop (every 10 seconds)
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._monitor_tick)
        self.monitor_timer.start(10000)

        # 6. Periodic status log (every 60 seconds)
        self.status_log_timer = QTimer(self)
        self.status_log_timer.timeout.connect(self._print_cli_status)
        self.status_log_timer.start(60000)

        self.log(f"Server started on host: {get_device_name()} | Monitoring {len(self.favorites)} creators")
        if self.sync_mgr.backend:
            self.log("Sync backend configured. Performing initial sync...")
            self.sync_mgr.sync_now_async()

    def log(self, message: str):
        t_str = time.strftime("%H:%M:%S")
        entry = {"time": t_str, "message": message}
        self.logs.append(entry)
        if len(self.logs) > 300:
            self.logs.pop(0)
        print(f"[{t_str}] {message}")

    def _load_favorites(self) -> dict:
        fav_file = os.path.join(DATA_DIR, "favorites.json")
        if os.path.exists(fav_file):
            try:
                with open(fav_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {u: True for u in data}
                    return data
            except Exception:
                pass
        return {}

    def _load_settings(self) -> dict:
        set_file = os.path.join(DATA_DIR, "settings.json")
        default_s = {"like_delay_ms": 100, "randomization_ms": 50}
        if os.path.exists(set_file):
            try:
                with open(set_file, "r") as f:
                    data = json.load(f)
                    default_s.update(data)
            except Exception:
                pass
        return default_s

    # --- Live Checking Worker Pool ---

    def _get_or_create_worker(self):
        from tiktok_live_auto_liker_tapper import CheckerWorker
        worker = CheckerWorker(parent=self)
        worker.status_checked.connect(self._on_user_status_checked)
        worker.ready.connect(self._on_worker_ready)
        self.workers.append(worker)
        return worker

    def _on_worker_ready(self, worker):
        if worker not in self.idle_workers:
            self.idle_workers.append(worker)
        self._process_queue()

    def _process_queue(self):
        while self.check_queue and self.idle_workers:
            user = self.check_queue.pop(0)
            worker = self.idle_workers.pop(0)
            worker.check_user(user)

    def _monitor_tick(self):
        # Refresh checker pool if empty
        if not self.workers:
            for _ in range(3):
                w = self._get_or_create_worker()
                self.idle_workers.append(w)

        # Enqueue favorite creators not already in check queue
        for user in self.favorites.keys():
            if user not in self.check_queue:
                self.check_queue.append(user)
        self._process_queue()

        # Check for ended streams
        ended = [un for un, s in self.active_streams.items() if not s.is_active]
        for un in ended:
            self.log(f"[STREAM ENDED] @{un} live stream ended.")
            tab = self.active_streams.pop(un)
            tab.cleanup()
            self.known_live.discard(un)

    def _on_user_status_checked(self, username: str, is_live: bool, avatar_url: str, is_error: bool):
        if avatar_url:
            self.avatars[username] = avatar_url

        if is_error:
            return

        was_live = username in self.known_live

        if is_live:
            self.known_live.add(username)
            if not was_live:
                self.log(f"[LIVE] @{username} is LIVE!")
                tapper_enabled = self.favorites.get(username, True)
                if isinstance(tapper_enabled, dict):
                    tapper_enabled = tapper_enabled.get("tapper_enabled", True)
                if tapper_enabled and username not in self.active_streams:
                    self.log(f"[TAPPING STARTED] Mounting stream and starting auto-tapper for @{username}...")
                    tab = HeadlessStreamTab(username, self.settings, tapper_enabled=True, stats_mgr=self.stats_mgr, parent=self)
                    self.active_streams[username] = tab
        else:
            self.known_live.discard(username)
            if was_live and username in self.active_streams:
                self.log(f"[STREAM ENDED] @{username} is now offline.")
                tab = self.active_streams.pop(username)
                tab.cleanup()

    # --- Sync Events ---

    def _on_sync_completed(self, msg: str, has_changes: bool):
        self.log(f"[SYNC] {msg}")
        if has_changes:
            self.favorites = self._load_favorites()
            self.settings = self._load_settings()
            for stream in self.active_streams.values():
                stream.update_settings(self.settings)

    def _on_sync_failed(self, err: str):
        self.log(f"[SYNC ERROR] {err}")

    def _on_cookies_updated(self, cookies: list):
        UniversalWebView.inject_cookies_into_profile(cookies, USER_DATA_DIR)
        if cookies:
            self.log(f"[AUTH] Received updated session ({len(cookies)} cookies). Profile updated.")
        else:
            self.log("[AUTH] TikTok session cleared.")

    # --- CLI Status ---

    def _print_cli_status(self):
        uptime = int(time.time() - self.start_time)
        active_cnt = len(self.active_streams)
        live_cnt = len(self.known_live)
        total_cnt = len(self.favorites)
        self.log(f"[STATUS] Uptime: {uptime}s | Monitored: {total_cnt} | Live: {live_cnt} | Tapping: {active_cnt}")

    # --- Web Dashboard API Methods ---

    def get_status_summary(self) -> dict:
        active_list = []
        for un, tab in self.active_streams.items():
            active_list.append({
                "username": un,
                "is_live": True,
                "tapper_enabled": tab.tapper_enabled,
                "is_muted": tab.is_muted,
                "avatar_url": self.avatars.get(un, ""),
                "base_delay_ms": tab.settings.get("like_delay_ms", 100),
                "verified_likes": tab.verified_likes,
                "taps_dispatched": tab.taps_dispatched,
                "live_rate": tab.live_rate,
                "room_likes": tab.room_likes,
                "duration_seconds": int(time.time() - tab.start_time)
            })

        return {
            "uptime": int(time.time() - self.start_time),
            "monitored_count": len(self.favorites),
            "live_count": len(self.known_live),
            "tapping_count": len(self.active_streams),
            "sync_status": self.sync_mgr.last_sync_status,
            "active_streams": active_list
        }

    def get_favorites_list(self) -> list:
        res = []
        for un, info in self.favorites.items():
            tapper = info.get("tapper_enabled", True) if isinstance(info, dict) else bool(info)
            muted = info.get("is_muted", True) if isinstance(info, dict) else True
            res.append({
                "username": un,
                "tapper_enabled": tapper,
                "is_muted": muted,
                "is_live": un in self.known_live,
                "avatar_url": self.avatars.get(un, "")
            })
        return res

    def add_favorite(self, username: str):
        if username not in self.favorites:
            self.favorites[username] = True
            with open(os.path.join(DATA_DIR, "favorites.json"), "w") as f:
                json.dump(self.favorites, f, indent=2)
            self.log(f"[WEB] Added @{username} to favorites.")
            self.sync_mgr.record_local_change()

    def remove_favorite(self, username: str):
        if username in self.favorites:
            del self.favorites[username]
            with open(os.path.join(DATA_DIR, "favorites.json"), "w") as f:
                json.dump(self.favorites, f, indent=2)
            self.sync_mgr.record_deletion(username)
            if username in self.active_streams:
                tab = self.active_streams.pop(username)
                tab.cleanup()
            self.log(f"[WEB] Removed @{username} from favorites.")

    def toggle_favorite_field(self, username: str, field: str):
        if username in self.favorites:
            curr = self.favorites[username]
            if isinstance(curr, bool):
                curr = {"tapper_enabled": curr, "is_muted": True, "updated_at": time.time()}
            elif isinstance(curr, dict):
                curr = dict(curr)

            if field == "tapper":
                curr["tapper_enabled"] = not curr.get("tapper_enabled", True)
                if username in self.active_streams:
                    self.active_streams[username].set_tapper_enabled(curr["tapper_enabled"])
            elif field == "mute":
                curr["is_muted"] = not curr.get("is_muted", True)

            curr["updated_at"] = time.time()
            self.favorites[username] = curr
            with open(os.path.join(DATA_DIR, "favorites.json"), "w") as f:
                json.dump(self.favorites, f, indent=2)
            self.sync_mgr.record_local_change()

    def get_settings(self) -> dict:
        return self.settings

    def update_settings(self, new_s: dict):
        self.settings.update(new_s)
        self.settings["updated_at"] = time.time()
        with open(os.path.join(DATA_DIR, "settings.json"), "w") as f:
            json.dump(self.settings, f, indent=2)
        for s in self.active_streams.values():
            s.update_settings(self.settings)
        self.log(f"[WEB] Settings updated: Delay={self.settings.get('like_delay_ms')}ms, Rand={self.settings.get('randomization_ms')}ms")
        self.sync_mgr.record_local_change()

    def trigger_sync(self) -> str:
        self.log("[WEB] Manual sync triggered from Web Dashboard.")
        ok, msg = self.sync_mgr.sync_now()
        return msg

    def get_sync_config(self) -> dict:
        s = self.sync_mgr._read_settings()
        sync_cfg = s.get("sync", {})
        return {
            "enabled": bool(sync_cfg.get("enabled", False)),
            "method": sync_cfg.get("method", "folder"),
            "folder_path": sync_cfg.get("folder_path", ""),
            "webdav_url": sync_cfg.get("webdav_url", ""),
            "webdav_username": sync_cfg.get("webdav_username", ""),
            "webdav_password": sync_cfg.get("webdav_password", ""),
            "rest_url": sync_cfg.get("rest_url", ""),
            "rest_api_key": sync_cfg.get("rest_api_key", ""),
            "auto_sync_interval_s": int(sync_cfg.get("auto_sync_interval_s", 60)),
            "sync_cookies": bool(sync_cfg.get("sync_cookies", True)),
            "last_sync_time": self.sync_mgr.last_sync_time,
            "last_sync_status": self.sync_mgr.last_sync_status
        }

    def save_sync_config(self, cfg: dict) -> Tuple[bool, str]:
        s = self.sync_mgr._read_settings()
        s["sync"] = cfg
        self.sync_mgr._write_settings(s)
        self.sync_mgr.reload_config()
        self.log(f"[WEB] Sync configuration saved (Method: {cfg.get('method')}, Enabled: {cfg.get('enabled')})")
        return True, "Sync settings saved successfully"

    def test_sync_config(self, cfg: dict) -> Tuple[bool, str]:
        from sync_manager import create_backend
        backend = create_backend(cfg)
        if not backend:
            return False, "Could not create backend for the specified method."
        return backend.test_connection()

    def get_cookie_status(self) -> dict:
        cookies, updated_at = self.sync_mgr._read_cookies()
        session_val = ""
        for c in cookies:
            if c.get("name") == "sessionid":
                session_val = c.get("value", "")
                break
        is_auth = bool(session_val)
        masked = ""
        if session_val:
            if len(session_val) > 8:
                masked = session_val[:4] + "***" + session_val[-4:]
            else:
                masked = "***"
        return {
            "is_authenticated": is_auth,
            "cookie_count": len(cookies),
            "session_masked": masked,
            "updated_at": updated_at
        }

    def import_cookies(self, raw_input: str) -> Tuple[bool, str, int]:
        from sync_manager import parse_cookie_input
        cookies = parse_cookie_input(raw_input)
        if not cookies:
            return False, "No valid TikTok cookies or session ID found in input.", 0
        self.sync_mgr.update_local_cookies(cookies)
        self.log(f"[WEB] Imported {len(cookies)} TikTok cookies. Session authenticated!")
        return True, f"Successfully imported {len(cookies)} cookies!", len(cookies)

    def clear_cookies(self) -> Tuple[bool, str]:
        self.sync_mgr.clear_local_cookies()
        self.log("[WEB] TikTok session cleared.")
        return True, "Session cleared successfully"

    def get_recent_logs(self) -> list:
        return [f"[{entry['time']}] {entry['message']}" for entry in self.logs]

    def get_stats_kpis(self) -> dict:
        return self.stats_mgr.get_kpis()

    def get_stats_chart(self, days: int = 14) -> dict:
        return self.stats_mgr.get_daily_chart_data(days=days)

    def get_stats_leaderboard(self, limit: int = 10) -> list:
        return self.stats_mgr.get_streamer_leaderboard(limit=limit)

    def get_stats_sessions(self, limit: int = 50) -> list:
        return self.stats_mgr.get_recent_sessions(limit=limit)

    def export_stats_csv(self) -> str:
        return self.stats_mgr.export_csv()

    def cleanup(self):
        self.monitor_timer.stop()
        self.status_log_timer.stop()
        self.sync_mgr.stop()
        if hasattr(self, 'stats_mgr'):
            self.stats_mgr.save_now()
        if self.web_server:
            self.web_server.stop()
        for tab in self.active_streams.values():
            tab.cleanup()
        self.active_streams.clear()


def main():
    parser = argparse.ArgumentParser(description="TikTok Live Auto-Liker Headless Server")
    parser.add_argument("--port", type=int, default=8080, help="Web dashboard port (default: 8080)")
    parser.add_argument("--no-web", action="store_true", help="Disable the built-in web dashboard")
    parser.add_argument("--sync-only", action="store_true", help="Run a single sync cycle and exit immediately")
    args = parser.parse_args()

    if args.sync_only:
        print("Running one-time synchronization...")
        mgr = SyncManager(data_dir=DATA_DIR)
        ok, msg = mgr.sync_now()
        print(f"Sync result: {msg}")
        sys.exit(0 if ok else 1)

    app = QApplication(sys.argv)

    server = HeadlessServerManager(port=args.port, enable_web=not args.no_web)

    def handle_signal(sig, frame):
        print(f"\nReceived signal {sig}. Shutting down headless server...")
        server.cleanup()
        app.quit()
        if xvfb_proc:
            try: xvfb_proc.terminate()
            except Exception: pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("=" * 60)
    print("  TikTok Live Auto-Liker — Headless Server Running")
    print("=" * 60)
    if not args.no_web:
        print(f"  Web Dashboard: http://0.0.0.0:{args.port}")
    print(f"  Data Folder:   {DATA_DIR}")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
