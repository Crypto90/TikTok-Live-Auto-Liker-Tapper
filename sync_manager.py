"""Multi-device synchronization manager for TikTok Live Auto Liker.

Supports keeping favorites, settings, and toggles in sync across:
- macOS, Windows, Linux desktop apps, and Linux headless servers.

Backends:
1. FolderSyncBackend: Local or cloud-synced folder (Dropbox, OneDrive, Google Drive, Syncthing, SMB/NFS).
2. WebDAVSyncBackend: Remote WebDAV server (Nextcloud, ownCloud, Fastmail, Box) using urllib.
3. RestSyncBackend: REST API sync (self-hosted sync server or cloud endpoint).
"""

import os
import sys
import json
import time
import socket
import threading
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, Tuple, Callable

# Try importing PyQt6 for signals; provide pure Python fallback if not available
try:
    from PyQt6.QtCore import QObject, pyqtSignal
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False
    class QObject:
        def __init__(self, *args, **kwargs): pass
    def pyqtSignal(*args, **kwargs):
        class _Signal:
            def __init__(self): self._cbs = []
            def connect(self, cb): self._cbs.append(cb)
            def emit(self, *a, **kw):
                for cb in self._cbs:
                    try: cb(*a, **kw)
                    except Exception: pass
        return _Signal()


def get_device_name() -> str:
    try:
        return socket.gethostname() or sys.platform
    except Exception:
        return sys.platform


class SyncBundle:
    """Represents the serializable sync state."""
    VERSION = 1

    def __init__(self, settings: dict = None, favorites: dict = None, tombstones: dict = None, device_name: str = None):
        self.version = self.VERSION
        self.device_name = device_name or get_device_name()
        self.timestamp = time.time()
        self.settings = settings or {
            "like_delay_ms": 100,
            "randomization_ms": 50,
            "updated_at": time.time()
        }
        # Normalize favorites: username -> { tapper_enabled, is_muted, updated_at }
        self.favorites: Dict[str, dict] = {}
        if favorites:
            now = time.time()
            for k, v in favorites.items():
                if isinstance(v, bool):
                    self.favorites[k] = {
                        "tapper_enabled": v,
                        "is_muted": True,
                        "updated_at": now
                    }
                elif isinstance(v, dict):
                    self.favorites[k] = {
                        "tapper_enabled": bool(v.get("tapper_enabled", v.get("tapper", True))),
                        "is_muted": bool(v.get("is_muted", v.get("muted", True))),
                        "updated_at": float(v.get("updated_at", now))
                    }
        # Tombstones: username -> deleted_at timestamp
        self.tombstones: Dict[str, float] = tombstones or {}

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "device_name": self.device_name,
            "timestamp": self.timestamp,
            "settings": self.settings,
            "favorites": self.favorites,
            "tombstones": self.tombstones
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncBundle":
        b = cls(
            settings=data.get("settings"),
            favorites=data.get("favorites"),
            tombstones=data.get("tombstones"),
            device_name=data.get("device_name")
        )
        b.timestamp = float(data.get("timestamp", time.time()))
        return b


def merge_bundles(local: SyncBundle, remote: SyncBundle) -> Tuple[SyncBundle, bool, bool]:
    """
    Merge two sync bundles using Last-Write-Wins (LWW) with tombstones.
    Returns: (merged_bundle, local_changed, remote_changed)
    """
    merged = SyncBundle(device_name=local.device_name)
    local_changed = False
    remote_changed = False

    # 1. Merge tombstones (keep latest deletion timestamp for each)
    all_tomb_keys = set(local.tombstones.keys()) | set(remote.tombstones.keys())
    merged_tombstones: Dict[str, float] = {}
    for k in all_tomb_keys:
        t_loc = local.tombstones.get(k, 0.0)
        t_rem = remote.tombstones.get(k, 0.0)
        merged_tombstones[k] = max(t_loc, t_rem)

    # Clean old tombstones (> 60 days old) to prevent unbounded growth
    now = time.time()
    sixty_days_ago = now - (60 * 86400)
    # Only prune if the tombstone timestamp is in the modern epoch (> year 2020) and genuinely > 60 days old
    merged.tombstones = {
        k: v for k, v in merged_tombstones.items()
        if not (v > 1577836800 and v < sixty_days_ago)
    }
    if merged.tombstones != local.tombstones:
        local_changed = True
    if merged.tombstones != remote.tombstones:
        remote_changed = True

    # 2. Merge favorites
    all_fav_users = set(local.favorites.keys()) | set(remote.favorites.keys())
    merged_favs: Dict[str, dict] = {}

    for user in all_fav_users:
        loc_fav = local.favorites.get(user)
        rem_fav = remote.favorites.get(user)
        tomb_time = merged.tombstones.get(user, 0.0)

        best_fav = None
        if loc_fav and rem_fav:
            loc_time = float(loc_fav.get("updated_at", 0.0))
            rem_time = float(rem_fav.get("updated_at", 0.0))
            if loc_time >= rem_time:
                best_fav = loc_fav
                if rem_fav != loc_fav:
                    remote_changed = True
            else:
                best_fav = rem_fav
                if loc_fav != rem_fav:
                    local_changed = True
        elif loc_fav:
            best_fav = loc_fav
            remote_changed = True
        elif rem_fav:
            best_fav = rem_fav
            local_changed = True

        if best_fav:
            fav_time = float(best_fav.get("updated_at", 0.0))
            if tomb_time > 0 and tomb_time >= fav_time:
                # User is deleted
                if loc_fav:
                    local_changed = True
                if rem_fav:
                    remote_changed = True
            else:
                merged_favs[user] = best_fav

    merged.favorites = merged_favs

    # 3. Merge settings (higher updated_at wins)
    loc_s_time = float(local.settings.get("updated_at", 0.0))
    rem_s_time = float(remote.settings.get("updated_at", 0.0))
    if rem_s_time > loc_s_time:
        merged.settings = dict(remote.settings)
        local_changed = True
    else:
        merged.settings = dict(local.settings)
        if loc_s_time > rem_s_time:
            remote_changed = True

    merged.timestamp = time.time()
    return merged, local_changed, remote_changed


class BaseSyncBackend:
    """Abstract base for synchronization backends."""
    def test_connection(self) -> Tuple[bool, str]:
        raise NotImplementedError

    def fetch_bundle(self) -> Tuple[Optional[SyncBundle], Optional[str]]:
        raise NotImplementedError

    def push_bundle(self, bundle: SyncBundle) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError


class FolderSyncBackend(BaseSyncBackend):
    """Sync via local folder or cloud-synced folder (Dropbox, Google Drive, OneDrive, Syncthing, SMB/NFS)."""
    BUNDLE_FILENAME = "tiktok_live_sync_bundle.json"

    def __init__(self, folder_path: str):
        self.folder_path = os.path.abspath(os.path.expanduser(folder_path)) if folder_path else ""

    def test_connection(self) -> Tuple[bool, str]:
        if not self.folder_path:
            return False, "Folder path is empty."
        try:
            os.makedirs(self.folder_path, exist_ok=True)
            test_file = os.path.join(self.folder_path, ".sync_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return True, f"Writable access verified in {self.folder_path}"
        except Exception as e:
            return False, f"Folder access error: {e}"

    def fetch_bundle(self) -> Tuple[Optional[SyncBundle], Optional[str]]:
        if not self.folder_path:
            return None, "Folder path not configured."
        bundle_file = os.path.join(self.folder_path, self.BUNDLE_FILENAME)
        if not os.path.exists(bundle_file):
            return None, None  # No remote bundle yet; normal on first setup
        try:
            with open(bundle_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SyncBundle.from_dict(data), None
        except Exception as e:
            return None, f"Failed to read bundle from folder: {e}"

    def push_bundle(self, bundle: SyncBundle) -> Tuple[bool, Optional[str]]:
        if not self.folder_path:
            return False, "Folder path not configured."
        try:
            os.makedirs(self.folder_path, exist_ok=True)
            bundle_file = os.path.join(self.folder_path, self.BUNDLE_FILENAME)
            temp_file = bundle_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(bundle.to_dict(), f, indent=2)
            os.replace(temp_file, bundle_file)
            return True, None
        except Exception as e:
            return False, f"Failed to write bundle to folder: {e}"


class WebDAVSyncBackend(BaseSyncBackend):
    """Sync via WebDAV server (Nextcloud, ownCloud, Fastmail, Box, etc.)."""
    BUNDLE_FILENAME = "tiktok_live_sync_bundle.json"

    def __init__(self, server_url: str, username: str = "", password: str = ""):
        self.server_url = server_url.rstrip("/") if server_url else ""
        self.username = username
        self.password = password

    def _get_target_url(self) -> str:
        if self.server_url.endswith(".json"):
            return self.server_url
        return f"{self.server_url}/{self.BUNDLE_FILENAME}"

    def _build_request(self, url: str, data: bytes = None, method: str = "GET") -> urllib.request.Request:
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("User-Agent", "TikTokLiveAutoLiker-Sync/1.0")
        if self.username or self.password:
            import base64
            auth_str = f"{self.username}:{self.password}"
            encoded = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")
            req.add_header("Authorization", f"Basic {encoded}")
        return req

    def test_connection(self) -> Tuple[bool, str]:
        if not self.server_url:
            return False, "WebDAV URL is empty."
        try:
            url = self.server_url
            req = self._build_request(url, method="PROPFIND")
            req.add_header("Depth", "0")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 207):
                        return True, "WebDAV connection successful!"
            except urllib.error.HTTPError as e:
                if e.code in (405, 501):
                    get_req = self._build_request(url, method="GET")
                    with urllib.request.urlopen(get_req, timeout=10) as resp2:
                        return True, f"Connected (HTTP {resp2.status})"
                elif e.code == 401:
                    return False, "Authentication failed (401 Unauthorized)."
                elif e.code == 404:
                    return True, "Server reachable (URL path returned 404)."
                else:
                    return False, f"HTTP Error {e.code}: {e.reason}"
            return True, "WebDAV connection verified."
        except Exception as e:
            return False, f"WebDAV connection error: {e}"

    def fetch_bundle(self) -> Tuple[Optional[SyncBundle], Optional[str]]:
        if not self.server_url:
            return None, "WebDAV URL not configured."
        url = self._get_target_url()
        try:
            req = self._build_request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return SyncBundle.from_dict(data), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            return None, f"WebDAV HTTP error {e.code}: {e.reason}"
        except Exception as e:
            return None, f"WebDAV fetch error: {e}"

    def push_bundle(self, bundle: SyncBundle) -> Tuple[bool, Optional[str]]:
        if not self.server_url:
            return False, "WebDAV URL not configured."
        url = self._get_target_url()
        try:
            payload = json.dumps(bundle.to_dict(), indent=2).encode("utf-8")
            req = self._build_request(url, data=payload, method="PUT")
            req.add_header("Content-Type", "application/json; charset=utf-8")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201, 204):
                    return True, None
                return False, f"WebDAV returned status {resp.status}"
        except urllib.error.HTTPError as e:
            return False, f"WebDAV PUT failed ({e.code}): {e.reason}"
        except Exception as e:
            return False, f"WebDAV push error: {e}"


class RestSyncBackend(BaseSyncBackend):
    """Sync via REST API server (standalone sync_server.py or custom endpoint)."""
    def __init__(self, endpoint_url: str, api_key: str = ""):
        self.endpoint_url = endpoint_url.rstrip("/") if endpoint_url else ""
        self.api_key = api_key

    def _build_request(self, url: str, data: bytes = None, method: str = "GET") -> urllib.request.Request:
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("User-Agent", "TikTokLiveAutoLiker-Sync/1.0")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
            req.add_header("X-API-Key", self.api_key)
        return req

    def test_connection(self) -> Tuple[bool, str]:
        if not self.endpoint_url:
            return False, "REST endpoint URL is empty."
        try:
            url = f"{self.endpoint_url}/api/sync" if not self.endpoint_url.endswith("/api/sync") else self.endpoint_url
            req = self._build_request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True, "REST Sync server connected successfully!"
                return True, f"Connected with HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return False, "Invalid API Key (401 Unauthorized)."
            return False, f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            return False, f"REST connection failed: {e}"

    def fetch_bundle(self) -> Tuple[Optional[SyncBundle], Optional[str]]:
        if not self.endpoint_url:
            return None, "REST endpoint URL not configured."
        url = f"{self.endpoint_url}/api/sync" if not self.endpoint_url.endswith("/api/sync") else self.endpoint_url
        try:
            req = self._build_request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data or not isinstance(data, dict) or not data.get("favorites"):
                    return None, None
                return SyncBundle.from_dict(data), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            return None, f"REST HTTP error {e.code}: {e.reason}"
        except Exception as e:
            return None, f"REST fetch error: {e}"

    def push_bundle(self, bundle: SyncBundle) -> Tuple[bool, Optional[str]]:
        if not self.endpoint_url:
            return False, "REST endpoint URL not configured."
        url = f"{self.endpoint_url}/api/sync" if not self.endpoint_url.endswith("/api/sync") else self.endpoint_url
        try:
            payload = json.dumps(bundle.to_dict(), indent=2).encode("utf-8")
            req = self._build_request(url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json; charset=utf-8")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201, 204):
                    return True, None
                return False, f"REST push returned HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            return False, f"REST POST failed ({e.code}): {e.reason}"
        except Exception as e:
            return False, f"REST push error: {e}"


class SyncManager(QObject):
    """
    Coordinates local state persistence, conflict-free merging,
    debounced pushing, and periodic background synchronization.
    """
    sync_completed = pyqtSignal(str, bool)  # (status_message, has_local_changes)
    sync_failed = pyqtSignal(str)          # (error_message)

    def __init__(self, data_dir: str, parent=None):
        super().__init__(parent)
        self.data_dir = os.path.abspath(data_dir)
        self.favorites_file = os.path.join(self.data_dir, "favorites.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.sync_state_file = os.path.join(self.data_dir, "sync_state.json")

        self.lock = threading.Lock()
        self._sync_timer: Optional[threading.Timer] = None
        self._debounce_timer: Optional[threading.Timer] = None
        self._is_syncing = False
        self._stop_event = threading.Event()

        self.tombstones: Dict[str, float] = self._load_tombstones()
        self.last_sync_time: float = 0.0
        self.last_sync_status: str = "Not synced yet"

        self.backend: Optional[BaseSyncBackend] = None
        self.reload_config()

    # --- Configuration ---

    def reload_config(self):
        """Reload sync settings from settings.json."""
        with self.lock:
            settings = self._read_settings()
            sync_cfg = settings.get("sync", {})
            enabled = bool(sync_cfg.get("enabled", False))
            method = sync_cfg.get("method", "folder")  # folder | webdav | rest

            if not enabled:
                self.backend = None
                self._stop_sync_timer()
                return

            if method == "folder":
                self.backend = FolderSyncBackend(sync_cfg.get("folder_path", ""))
            elif method == "webdav":
                self.backend = WebDAVSyncBackend(
                    server_url=sync_cfg.get("webdav_url", ""),
                    username=sync_cfg.get("webdav_username", ""),
                    password=sync_cfg.get("webdav_password", "")
                )
            elif method == "rest":
                self.backend = RestSyncBackend(
                    endpoint_url=sync_cfg.get("rest_url", ""),
                    api_key=sync_cfg.get("rest_api_key", "")
                )
            else:
                self.backend = None

            interval = max(15, int(sync_cfg.get("auto_sync_interval_s", 60)))
            self._start_sync_timer(interval)

    # --- Tombstone & State Persistence ---

    def _load_tombstones(self) -> Dict[str, float]:
        if os.path.exists(self.sync_state_file):
            try:
                with open(self.sync_state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("tombstones", {})
            except Exception:
                pass
        return {}

    def _save_sync_state(self):
        try:
            with open(self.sync_state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "tombstones": self.tombstones,
                    "last_sync_time": self.last_sync_time,
                    "last_sync_status": self.last_sync_status
                }, f, indent=2)
        except Exception:
            pass

    def record_deletion(self, username: str):
        """Record a deletion tombstone when a user removes a favorite locally."""
        with self.lock:
            self.tombstones[username] = time.time()
            self._save_sync_state()
        self.schedule_debounced_push()

    def record_local_change(self):
        """Schedule a debounced push after local favorites or settings changes."""
        self.schedule_debounced_push()

    # --- Local Data Access Helpers ---

    def _read_settings(self) -> dict:
        default_settings = {
            "like_delay_ms": 100,
            "randomization_ms": 50,
            "updated_at": time.time()
        }
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_settings.update(data)
            except Exception:
                pass
        return default_settings

    def _read_favorites(self) -> dict:
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {u: True for u in data}
                    return data
            except Exception:
                pass
        return {}

    def _write_settings(self, settings: dict):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass

    def _write_favorites(self, favorites: dict):
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(favorites, f, indent=2)
        except Exception:
            pass

    def get_local_bundle(self) -> SyncBundle:
        """Create a SyncBundle from current local disk files."""
        settings = self._read_settings()
        favs = self._read_favorites()
        return SyncBundle(
            settings=settings,
            favorites=favs,
            tombstones=self.tombstones
        )

    # --- Synchronization Execution ---

    def sync_now(self) -> Tuple[bool, str]:
        """
        Perform a full two-way synchronization cycle.
        Thread-safe; can be called synchronously or from a background thread.
        """
        if self._is_syncing:
            return False, "Sync already in progress."

        with self.lock:
            if not self.backend:
                return False, "Sync is not enabled or configured."
            self._is_syncing = True

        try:
            # 1. Fetch remote bundle
            remote_bundle, err = self.backend.fetch_bundle()
            if err:
                self.last_sync_status = f"Fetch failed: {err}"
                self.sync_failed.emit(self.last_sync_status)
                return False, self.last_sync_status

            local_bundle = self.get_local_bundle()

            # 2. If no remote bundle exists yet, push local bundle to initialize remote
            if remote_bundle is None:
                success, push_err = self.backend.push_bundle(local_bundle)
                if not success:
                    self.last_sync_status = f"Init push failed: {push_err}"
                    self.sync_failed.emit(self.last_sync_status)
                    return False, self.last_sync_status
                self.last_sync_time = time.time()
                self.last_sync_status = f"Initialized remote sync ({len(local_bundle.favorites)} creators)"
                self._save_sync_state()
                self.sync_completed.emit(self.last_sync_status, False)
                return True, self.last_sync_status

            # 3. Merge local and remote bundles
            merged_bundle, local_changed, remote_changed = merge_bundles(local_bundle, remote_bundle)

            # 4. If local needs updates, save to disk
            if local_changed:
                current_settings = self._read_settings()
                sync_block = current_settings.get("sync", {})
                new_settings = dict(merged_bundle.settings)
                new_settings["sync"] = sync_block
                self._write_settings(new_settings)

                new_favs = {
                    u: info.get("tapper_enabled", True) if isinstance(info, dict) else bool(info)
                    for u, info in merged_bundle.favorites.items()
                }
                self._write_favorites(new_favs)

                self.tombstones = merged_bundle.tombstones
                self._save_sync_state()

            # 5. If remote needs updates, push merged bundle back to remote
            if remote_changed:
                push_ok, push_err = self.backend.push_bundle(merged_bundle)
                if not push_ok:
                    self.last_sync_status = f"Push merged changes failed: {push_err}"
                    self.sync_failed.emit(self.last_sync_status)
                    return False, self.last_sync_status

            self.last_sync_time = time.time()
            fav_count = len(merged_bundle.favorites)
            if local_changed and remote_changed:
                msg = f"Synced & merged {fav_count} creators (bidirectional)"
            elif local_changed:
                msg = f"Synced: pulled {fav_count} creators from cloud"
            elif remote_changed:
                msg = f"Synced: pushed updates to cloud ({fav_count} creators)"
            else:
                msg = f"In sync ({fav_count} creators up to date)"

            self.last_sync_status = msg
            self._save_sync_state()
            self.sync_completed.emit(msg, local_changed)
            return True, msg

        except Exception as e:
            err_msg = f"Sync exception: {e}"
            self.last_sync_status = err_msg
            self.sync_failed.emit(err_msg)
            return False, err_msg
        finally:
            with self.lock:
                self._is_syncing = False

    def sync_now_async(self, callback: Optional[Callable[[bool, str], None]] = None):
        """Run sync_now on a background thread."""
        def _run():
            success, msg = self.sync_now()
            if callback:
                try: callback(success, msg)
                except Exception: pass
        t = threading.Thread(target=_run, daemon=True)
        t.start()

    # --- Timers & Debounce ---

    def schedule_debounced_push(self, delay_s: float = 2.0):
        """Schedule a background sync push after local changes have stopped for delay_s."""
        if not self.backend:
            return
        if self._debounce_timer:
            self._debounce_timer.cancel()

        def _do_push():
            if not self._stop_event.is_set():
                self.sync_now_async()

        self._debounce_timer = threading.Timer(delay_s, _do_push)
        self._debounce_timer.daemon = True
        self._debounce_timer.start()

    def _start_sync_timer(self, interval_s: int):
        self._stop_sync_timer()
        if interval_s <= 0 or not self.backend:
            return

        def _tick():
            if self._stop_event.is_set():
                return
            self.sync_now_async()
            if not self._stop_event.is_set():
                self._sync_timer = threading.Timer(interval_s, _tick)
                self._sync_timer.daemon = True
                self._sync_timer.start()

        self._sync_timer = threading.Timer(interval_s, _tick)
        self._sync_timer.daemon = True
        self._sync_timer.start()

    def _stop_sync_timer(self):
        if self._sync_timer:
            self._sync_timer.cancel()
            self._sync_timer = None
        if self._debounce_timer:
            self._debounce_timer.cancel()
            self._debounce_timer = None

    def stop(self):
        """Stop all background sync activity."""
        self._stop_event.set()
        self._stop_sync_timer()
