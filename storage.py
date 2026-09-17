"""Crash-safe JSON files (favorites, settings, cookies, sync state, stats).

Writing straight into a file leaves it truncated if the app crashes or the power fails mid-write.
The loaders then silently fell back to empty data, and the next save made the loss permanent.
Here every write goes to a temporary file that atomically replaces the original, the previous good
version is kept as <file>.bak, and reads fall back to that copy when the file is damaged.
"""

import json
import logging
import os
import shutil
import threading
import time

log = logging.getLogger("storage")

_locks = {}
_locks_guard = threading.Lock()


def _lock_for(path: str) -> threading.RLock:
    # The sync thread and the UI write the same files; serialize writers within the process
    key = os.path.normcase(os.path.abspath(path))
    with _locks_guard:
        return _locks.setdefault(key, threading.RLock())


def backup_path(path: str) -> str:
    return path + ".bak"


def _load(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_json(path: str, default=None):
    """Contents of a JSON file; its backup if the file exists but is damaged; otherwise `default`."""
    with _lock_for(path):
        if not os.path.exists(path):
            return default
        try:
            return _load(path)
        except (OSError, ValueError) as exc:
            log.error("Could not read %s: %s", path, exc)
        backup = backup_path(path)
        if os.path.exists(backup):
            try:
                data = _load(backup)
                log.warning("Recovered %s from its backup copy", path)
                return data
            except (OSError, ValueError) as exc:
                log.error("Backup %s is damaged too: %s", backup, exc)
        return default


def write_json(path: str, data, indent: int = 2, ensure_ascii: bool = True):
    """Atomically replace `path` with `data`, keeping the previous readable version as a backup."""
    with _lock_for(path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            f.flush()
            os.fsync(f.fileno())

        if os.path.exists(path):
            try:
                _load(path)
                shutil.copyfile(path, backup_path(path))
            except (OSError, ValueError):
                pass  # never let a damaged file overwrite the last good backup

        for attempt in range(5):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                # Windows: antivirus or indexer can briefly hold the file open
                if attempt == 4:
                    raise
                time.sleep(0.05 * (attempt + 1))
