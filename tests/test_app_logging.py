import logging
import sys
import threading

import pytest

import app_logging


@pytest.fixture
def logging_setup(tmp_path):
    root = logging.getLogger()
    handlers, level = list(root.handlers), root.level
    hooks = (sys.excepthook, threading.excepthook)
    log_dir = app_logging.setup_logging(str(tmp_path))
    yield tmp_path / "logs"
    for h in root.handlers:
        if h not in handlers:
            h.close()
    root.handlers[:] = handlers
    root.setLevel(level)
    sys.excepthook, threading.excepthook = hooks
    assert log_dir


def log_text(log_dir):
    for h in logging.getLogger().handlers:
        h.flush()
    return (log_dir / app_logging.LOG_FILE_NAME).read_text(encoding="utf-8")


def test_errors_reported_through_logging_are_saved(logging_setup):
    # qtwebview2 reports exceptions raised inside JS callbacks this way
    try:
        raise NameError("name 'dt' is not defined")
    except NameError as exc:
        logging.getLogger("qtwebview2").error(f"Error processing JS callback: {exc}", exc_info=True)
    text = log_text(logging_setup)
    assert "Error processing JS callback: name 'dt' is not defined" in text
    assert "Traceback" in text


def test_uncaught_and_thread_exceptions_are_saved(logging_setup, monkeypatch):
    monkeypatch.setattr(sys, "stderr", None)  # packaged app: no console
    try:
        raise ValueError("uncaught in slot")
    except ValueError:
        sys.excepthook(*sys.exc_info())

    def fail():
        raise RuntimeError("worker thread died")

    t = threading.Thread(target=fail, name="sync-worker")
    t.start()
    t.join()
    text = log_text(logging_setup)
    assert "uncaught in slot" in text
    assert "Unhandled exception in thread sync-worker" in text and "worker thread died" in text


def test_setup_is_idempotent(logging_setup):
    app_logging.setup_logging(str(logging_setup.parent))
    file_handlers = [h for h in logging.getLogger().handlers
                     if getattr(h, "baseFilename", "").endswith(app_logging.LOG_FILE_NAME)]
    assert len(file_handlers) == 1
