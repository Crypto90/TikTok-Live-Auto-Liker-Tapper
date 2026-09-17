"""Persistent error log for the desktop app and the headless server.

The packaged app has no console, so errors were invisible: uncaught exceptions, errors that
qtwebview2 catches and reports through `logging` (e.g. a crash inside a stats callback), thread
errors and Qt warnings. They all go to <data dir>/logs/autoliker.log; hard crashes of the Python
process go to crash.log.
"""

import faulthandler
import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "autoliker.log"
CRASH_FILE_NAME = "crash.log"

_crash_file = None


def log_dir_for(data_dir: str) -> str:
    return os.path.join(data_dir, "logs")


def setup_logging(data_dir: str, max_bytes: int = 1_000_000, backups: int = 3) -> str:
    """Install the log file, exception hooks and crash dump. Safe to call more than once."""
    global _crash_file
    log_dir = log_dir_for(data_dir)
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    log_path = os.path.join(log_dir, LOG_FILE_NAME)
    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == os.path.abspath(log_path) for h in root.handlers):
        handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"))
        root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Replacing sys.excepthook also stops PyQt from aborting the whole app on an exception in a slot
    sys.excepthook = _log_uncaught
    threading.excepthook = _log_thread_exception

    if _crash_file is None:
        _crash_file = open(os.path.join(log_dir, CRASH_FILE_NAME), "a", encoding="utf-8")
        faulthandler.enable(file=_crash_file, all_threads=True)

    logging.getLogger("app").info("Logging started (Python %s, %s)", sys.version.split()[0], sys.platform)
    return log_dir


def _log_uncaught(exc_type, exc, tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return
    logging.getLogger("uncaught").error("Unhandled exception", exc_info=(exc_type, exc, tb))
    if sys.stderr:
        sys.__excepthook__(exc_type, exc, tb)


def _log_thread_exception(args):
    if issubclass(args.exc_type, SystemExit):
        return
    name = args.thread.name if args.thread else "unknown"
    logging.getLogger("thread").error("Unhandled exception in thread %s", name,
                                      exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
