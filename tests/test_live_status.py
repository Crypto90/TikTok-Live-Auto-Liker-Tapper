import io
import json
import time
import urllib.error

import pytest

from live_status import LiveStatusError, fetch_live_status


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def opener_returning(payload):
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return lambda request, timeout: Response(body)


def opener_raising(exc):
    def opener(request, timeout):
        raise exc
    return opener


def api(status=None, code=0, avatar="https://p16/avatar.jpg"):
    data = {"user": {"roomId": "1", "status": status, "avatarThumb": avatar}, "liveRoom": {"status": status}}
    return {"statusCode": code, "data": data}


def test_live_and_offline():
    live = fetch_live_status("a", opener=opener_returning(api(status=2)))
    assert live.is_live and live.avatar_url == "https://p16/avatar.jpg"
    assert not fetch_live_status("a", opener=opener_returning(api(status=4))).is_live


def test_unknown_user_is_not_an_error():
    result = fetch_live_status("nobody", opener=opener_returning({"statusCode": 19881007, "message": "user_not_found"}))
    assert not result.is_live and not result.exists


def test_username_is_url_encoded():
    seen = {}

    def opener(request, timeout):
        seen["url"] = request.full_url
        return Response(json.dumps(api(status=4)).encode())

    fetch_live_status("a&b=c", opener=opener)
    assert "uniqueId=a%26b%3Dc" in seen["url"]


@pytest.mark.parametrize("opener, blocked", [
    (opener_raising(urllib.error.HTTPError("u", 429, "Too Many", {}, None)), True),
    (opener_raising(urllib.error.HTTPError("u", 403, "Forbidden", {}, None)), True),
    (opener_raising(urllib.error.HTTPError("u", 500, "Error", {}, None)), False),
    (opener_raising(urllib.error.URLError("offline")), False),
    (opener_returning(b"<html>captcha</html>"), True),
    (opener_returning({"statusCode": 0, "data": {}}), True),
    (opener_returning({"statusCode": 10101, "message": "odd"}), False),
])
def test_untrustworthy_answers_raise(opener, blocked):
    with pytest.raises(LiveStatusError) as err:
        fetch_live_status("a", opener=opener)
    assert err.value.blocked is blocked


# ---------------------------------------------------------------- LiveChecker (Qt)

@pytest.fixture
def gui(monkeypatch):
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtCore import QCoreApplication, QObject, QTimer, pyqtSignal
    app_module = pytest.importorskip("tiktok_live_auto_liker_tapper")
    qt_app = QCoreApplication.instance() or QCoreApplication([])

    created = []

    class FakePageWorker(QObject):
        status_checked = pyqtSignal(str, bool, str, bool)
        ready = pyqtSignal(object)

        def __init__(self, parent=None):
            super().__init__(parent)
            created.append(self)

        def check_user(self, username):
            def finish():
                self.status_checked.emit(username, True, "page-avatar", False)
                self.ready.emit(self)
            QTimer.singleShot(0, finish)

        def cleanup(self):
            pass

    monkeypatch.setattr(app_module, "CheckerWorker", FakePageWorker)
    return app_module, qt_app, created


def collect(checker, qt_app, expected, timeout=5.0):
    results = []
    checker.status_checked.connect(lambda *args: results.append(args))
    return results, lambda: _pump(qt_app, results, expected, timeout)


def _pump(qt_app, results, expected, timeout):
    deadline = time.time() + timeout
    while len(results) < expected and time.time() < deadline:
        qt_app.processEvents()
        time.sleep(0.005)
    return results


def test_checker_uses_api_without_creating_browsers(gui, monkeypatch):
    app_module, qt_app, created = gui
    from live_status import LiveStatus
    monkeypatch.setattr(app_module, "fetch_live_status",
                        lambda u: LiveStatus(is_live=(u == "on"), avatar_url=f"{u}.jpg"))
    checker = app_module.LiveChecker()
    results, wait = collect(checker, qt_app, 2)
    checker.check_users(["on", "off"])
    assert sorted(wait()) == [("off", False, "off.jpg", False), ("on", True, "on.jpg", False)]
    assert created == []
    checker.cleanup()


def test_checker_falls_back_to_page_and_pauses_api_when_blocked(gui, monkeypatch):
    app_module, qt_app, created = gui
    calls = []

    def blocked(username):
        calls.append(username)
        raise LiveStatusError("HTTP 429", blocked=True)

    monkeypatch.setattr(app_module, "fetch_live_status", blocked)
    checker = app_module.LiveChecker(pool_size=2)
    results, wait = collect(checker, qt_app, 1)
    checker.check_users(["creator"])
    assert wait() == [("creator", True, "page-avatar", False)]
    assert len(created) == 1 and calls == ["creator"]

    results.clear()
    checker.check_users(["creator"])  # API paused: straight to the page check
    assert _pump(qt_app, results, 1, 5.0) == [("creator", True, "page-avatar", False)]
    assert calls == ["creator"]
    checker.cleanup()


def test_min_interval_skips_recently_checked(gui, monkeypatch):
    app_module, qt_app, _ = gui
    from live_status import LiveStatus
    calls = []
    monkeypatch.setattr(app_module, "fetch_live_status", lambda u: calls.append(u) or LiveStatus(is_live=False))
    checker = app_module.LiveChecker()
    results, wait = collect(checker, qt_app, 1)
    checker.check_users(["creator"], min_interval_s=30)
    wait()
    checker.check_users(["creator"], min_interval_s=30)
    _pump(qt_app, results, 2, 0.3)
    assert calls == ["creator"]
    checker.check_users(["creator"])  # desktop app's regular cycle doesn't skip
    _pump(qt_app, results, 2, 5.0)
    assert calls == ["creator", "creator"]
    checker.cleanup()
