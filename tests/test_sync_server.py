import http.client
import json
import threading
from http.server import HTTPServer

import pytest

import sync_server


def test_refuses_public_bind_without_api_key():
    with pytest.raises(SystemExit):
        sync_server.run_server(host="0.0.0.0", port=0, api_key=None)


@pytest.fixture
def running(tmp_path, monkeypatch):
    monkeypatch.setattr(sync_server, "API_KEY", "server-key")
    monkeypatch.setattr(sync_server, "DATA_FILE", str(tmp_path / "sync_data.json"))
    httpd = HTTPServer(("127.0.0.1", 0), sync_server.SyncHTTPRequestHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


def get(port, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", "/api/sync", headers=headers or {})
    resp = conn.getresponse()
    resp.read()
    conn.close()
    return resp


def test_api_key_required_and_no_cors(running):
    assert get(running).status == 401
    assert get(running, {"Authorization": "Bearer wrong"}).status == 401
    ok = get(running, {"Authorization": "Bearer server-key"})
    assert ok.status == 200
    assert ok.getheader("Access-Control-Allow-Origin") is None
    assert get(running, {"X-API-Key": "server-key"}).status == 200


def test_server_merge_keeps_encrypted_cookies(running):
    payload = {
        "version": 1, "timestamp": 1.0, "settings": {"updated_at": 1.0},
        "favorites": {"a": {"tapper_enabled": True, "is_muted": True, "updated_at": 1.0}}, "tombstones": {},
        "cookies": [], "cookies_encrypted": {"v": 1, "data": "opaque"}, "cookies_updated_at": 5.0, "sessions": [],
    }
    for _ in range(2):  # second push goes through the server-side merge
        conn = http.client.HTTPConnection("127.0.0.1", running, timeout=10)
        conn.request("POST", "/api/sync", body=json.dumps(payload), headers={"X-API-Key": "server-key", "Content-Type": "application/json"})
        assert conn.getresponse().status == 200
        conn.close()
    with open(sync_server.DATA_FILE) as f:
        stored = json.load(f)
    assert stored["cookies_encrypted"] == {"v": 1, "data": "opaque"}
