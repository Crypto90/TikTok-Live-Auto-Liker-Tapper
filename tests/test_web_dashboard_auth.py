import http.client
import json

import pytest

import web_server
from web_server import HeadlessWebServer, load_or_create_access_token

TOKEN = "test-token-123"


class FakeRunner:
    def __init__(self):
        self.added = []

    def get_status_summary(self):
        return {"active_streams": []}

    def add_favorite(self, username):
        self.added.append(username)


@pytest.fixture
def server():
    runner = FakeRunner()
    srv = HeadlessWebServer(host="127.0.0.1", port=0, runner_ref=runner, access_token=TOKEN)
    srv.start()
    yield srv, runner
    srv.stop()


def request(srv, method, path, body=None, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", srv.port, timeout=10)
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {"Content-Type": "application/json"} if data else {}
    hdrs.update(headers or {})
    conn.request(method, path, body=data, headers=hdrs)
    resp = conn.getresponse()
    payload = resp.read()
    conn.close()
    return resp, payload


def login_cookie(srv):
    resp, _ = request(srv, "POST", "/api/login", {"token": TOKEN})
    assert resp.status == 200
    set_cookie = resp.getheader("Set-Cookie")
    assert "HttpOnly" in set_cookie and "SameSite=Strict" in set_cookie
    return set_cookie.split(";")[0]


def test_page_is_public_but_api_requires_login(server):
    srv, _ = server
    resp, body = request(srv, "GET", "/")
    assert resp.status == 200 and b"Dashboard Login" in body
    assert resp.getheader("X-Frame-Options") == "DENY"
    assert resp.getheader("Access-Control-Allow-Origin") is None

    resp, _ = request(srv, "GET", "/api/status")
    assert resp.status == 401
    resp, body = request(srv, "GET", "/api/auth")
    assert json.loads(body) == {"authenticated": False}


def test_wrong_token_rejected(server):
    srv, _ = server
    resp, _ = request(srv, "POST", "/api/login", {"token": "nope"})
    assert resp.status == 401
    assert resp.getheader("Set-Cookie") is None


def test_session_cookie_and_bearer_token_grant_access(server):
    srv, _ = server
    cookie = login_cookie(srv)
    assert TOKEN not in cookie  # the cookie holds a derived value, not the token itself
    resp, _ = request(srv, "GET", "/api/status", headers={"Cookie": cookie})
    assert resp.status == 200
    resp, _ = request(srv, "GET", "/api/status", headers={"Authorization": f"Bearer {TOKEN}"})
    assert resp.status == 200
    resp, body = request(srv, "GET", "/api/auth", headers={"Cookie": cookie})
    assert json.loads(body) == {"authenticated": True}


def test_cross_site_requests_blocked(server):
    srv, runner = server
    cookie = login_cookie(srv)
    resp, _ = request(srv, "POST", "/api/favorites/add", {"username": "someone"},
                      headers={"Cookie": cookie, "Origin": "http://evil.example"})
    assert resp.status == 403
    resp, _ = request(srv, "POST", "/api/favorites/add", {"username": "someone"},
                      headers={"Cookie": cookie, "Sec-Fetch-Site": "cross-site"})
    assert resp.status == 403
    resp, _ = request(srv, "POST", "/api/favorites/add", {"username": "someone"},
                      headers={"Cookie": cookie, "Origin": f"http://127.0.0.1:{srv.port}", "Sec-Fetch-Site": "same-origin"})
    assert resp.status == 200 and runner.added == ["someone"]


def test_invalid_username_and_oversized_body(server):
    srv, runner = server
    auth = {"Authorization": f"Bearer {TOKEN}"}
    resp, _ = request(srv, "POST", "/api/favorites/add", {"username": "<img src=x onerror=alert(1)>"}, headers=auth)
    assert resp.status == 400 and runner.added == []

    conn = http.client.HTTPConnection("127.0.0.1", srv.port, timeout=10)
    conn.putrequest("POST", "/api/favorites/add")
    conn.putheader("Authorization", f"Bearer {TOKEN}")
    conn.putheader("Content-Length", str(web_server.MAX_BODY_BYTES + 1))
    conn.endheaders()
    assert conn.getresponse().status == 413
    conn.close()


def test_no_cors_preflight(server):
    srv, _ = server
    resp, _ = request(srv, "OPTIONS", "/api/status", headers={"Origin": "http://evil.example"})
    assert resp.status != 204
    assert resp.getheader("Access-Control-Allow-Origin") is None


def test_runner_failures_return_error_responses():
    class SlowRunner:
        def get_status_summary(self):
            raise TimeoutError("main thread busy")

        def get_favorites_list(self):
            raise KeyError("bug")

    srv = HeadlessWebServer(host="127.0.0.1", port=0, runner_ref=SlowRunner(), access_token=TOKEN)
    srv.start()
    try:
        auth = {"Authorization": f"Bearer {TOKEN}"}
        resp, body = request(srv, "GET", "/api/status", headers=auth)
        assert resp.status == 503 and json.loads(body)["error"]
        resp, _ = request(srv, "GET", "/api/favorites", headers=auth)
        assert resp.status == 500
        resp, _ = request(srv, "GET", "/api/auth")
        assert resp.status == 200  # server keeps serving afterwards
    finally:
        srv.stop()


def test_server_requires_token():
    with pytest.raises(ValueError):
        HeadlessWebServer(access_token="")


def test_login_url_uses_fragment():
    srv = HeadlessWebServer(host="0.0.0.0", port=8080, access_token="abc")
    assert srv.login_url == "http://127.0.0.1:8080/#token=abc"


def test_access_token_generated_once_and_env_override(tmp_path, monkeypatch):
    monkeypatch.delenv(web_server.TOKEN_ENV_VAR, raising=False)
    first = load_or_create_access_token(str(tmp_path))
    assert len(first) >= 32
    assert load_or_create_access_token(str(tmp_path)) == first
    monkeypatch.setenv(web_server.TOKEN_ENV_VAR, "from-env")
    assert load_or_create_access_token(str(tmp_path)) == "from-env"
