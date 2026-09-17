import http.client
import json
import threading
import time

import pytest

QtCore = pytest.importorskip("PyQt6.QtCore")


@pytest.fixture(scope="module")
def qt_app():
    return QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])


def run_in_worker(qt_app, target, timeout=5.0):
    """Run target on a worker thread while the main thread keeps processing Qt events."""
    outcome = {}

    def worker():
        try:
            outcome["result"] = target()
        except BaseException as exc:
            outcome["error"] = exc

    thread = threading.Thread(target=worker)
    thread.start()
    deadline = time.time() + timeout
    while thread.is_alive() and time.time() < deadline:
        qt_app.processEvents()
        time.sleep(0.005)
    thread.join(1)
    assert not thread.is_alive(), "worker did not finish"
    return outcome


def test_call_from_worker_runs_on_main_thread(headless_module, qt_app):
    dispatcher = headless_module.MainThreadDispatcher()
    main_thread = threading.get_ident()
    seen = {}

    def work(value):
        seen["thread"] = threading.get_ident()
        return value * 2

    outcome = run_in_worker(qt_app, lambda: dispatcher.call(work, 21))
    assert outcome == {"result": 42}
    assert seen["thread"] == main_thread


def test_errors_reach_the_calling_thread(headless_module, qt_app):
    dispatcher = headless_module.MainThreadDispatcher()

    def boom():
        raise ValueError("nope")

    outcome = run_in_worker(qt_app, lambda: dispatcher.call(boom))
    assert isinstance(outcome["error"], ValueError)


def test_timeout_when_main_thread_is_busy(headless_module, qt_app):
    dispatcher = headless_module.MainThreadDispatcher()
    ran = []
    result = {}
    thread = threading.Thread(target=lambda: result.update(
        error=pytest.raises(TimeoutError, dispatcher.call, ran.append, 1, timeout=0.2)))
    thread.start()
    thread.join(2)  # main thread deliberately not processing events
    assert "error" in result
    qt_app.processEvents()
    assert ran == []  # the abandoned job does not run later


def test_close_releases_waiting_callers(headless_module, qt_app):
    dispatcher = headless_module.MainThreadDispatcher()
    result = {}

    def call():
        start = time.time()
        try:
            dispatcher.call(lambda: None, timeout=10)
        except RuntimeError:
            result["released_after"] = time.time() - start

    thread = threading.Thread(target=call)
    thread.start()
    time.sleep(0.2)
    dispatcher.close()
    thread.join(2)
    assert result["released_after"] < 2
    later = run_in_worker(qt_app, lambda: dispatcher.call(lambda: None))
    assert isinstance(later["error"], RuntimeError)


def test_proxy_routes_calls(headless_module, qt_app):
    class Runner:
        port = 8080

        def __init__(self):
            self.threads = {}

        def add_favorite(self, username):
            self.threads["add_favorite"] = threading.get_ident()

        def trigger_sync(self):
            self.threads["trigger_sync"] = threading.get_ident()
            return "synced"

    runner = Runner()
    proxy = headless_module.DashboardRunnerProxy(runner, headless_module.MainThreadDispatcher())
    assert proxy.port == 8080

    worker_ids = {}

    def requests():
        worker_ids["id"] = threading.get_ident()
        proxy.add_favorite("someone")
        return proxy.trigger_sync()

    outcome = run_in_worker(qt_app, requests)
    assert outcome == {"result": "synced"}
    assert runner.threads["add_favorite"] == threading.get_ident()
    assert runner.threads["trigger_sync"] == worker_ids["id"]


def test_dashboard_request_runs_runner_on_main_thread(headless_module, qt_app):
    from web_server import HeadlessWebServer

    class Runner:
        def __init__(self):
            self.status_thread = None

        def get_status_summary(self):
            self.status_thread = threading.get_ident()
            return {"active_streams": []}

    runner = Runner()
    proxy = headless_module.DashboardRunnerProxy(runner, headless_module.MainThreadDispatcher())
    server = HeadlessWebServer(host="127.0.0.1", port=0, runner_ref=proxy, access_token="tok")
    server.start()
    try:
        def request():
            conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
            conn.request("GET", "/api/status", headers={"Authorization": "Bearer tok"})
            resp = conn.getresponse()
            body = json.loads(resp.read())
            conn.close()
            return resp.status, body

        outcome = run_in_worker(qt_app, request)
        assert outcome == {"result": (200, {"active_streams": []})}
        assert runner.status_thread == threading.get_ident()
    finally:
        server.stop()
