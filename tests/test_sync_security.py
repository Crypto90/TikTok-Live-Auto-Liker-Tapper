import json
import os

import pytest

pytest.importorskip("cryptography")

from sync_manager import (
    FolderSyncBackend,
    SyncManager,
    decrypt_cookies,
    encrypt_cookies,
    keep_local_secrets,
    public_settings,
)

COOKIES = [{"name": "sessionid", "value": "SECRET-SESSION-VALUE", "domain": ".tiktok.com", "path": "/"}]


def test_public_settings_strips_credentials_and_keep_local_secrets_restores_them():
    local = {
        "like_delay_ms": 200,
        "sync": {"method": "webdav", "webdav_password": "pw"},
        "notifications": {"notify_live": True, "discord_url": "https://discord/hook", "telegram_token": "tg", "telegram_chat_id": "1"},
    }
    clean = public_settings(local)
    assert "sync" not in clean
    assert clean["notifications"] == {"notify_live": True}

    incoming = {"like_delay_ms": 250, "notifications": {"notify_live": False}, "sync": {"webdav_password": "other-device"}}
    merged = keep_local_secrets(incoming, local)
    assert merged["like_delay_ms"] == 250
    assert merged["sync"] == local["sync"]
    assert merged["notifications"] == {"notify_live": False, "discord_url": "https://discord/hook", "telegram_token": "tg", "telegram_chat_id": "1"}


def test_cookie_encryption_round_trip_and_failures():
    blob = encrypt_cookies(COOKIES, "correct horse")
    assert "SECRET-SESSION-VALUE" not in json.dumps(blob)
    assert decrypt_cookies(blob, "correct horse") == COOKIES
    assert decrypt_cookies(blob, "wrong") is None
    tampered = dict(blob, data=blob["data"][:-4] + "AAAA")
    assert decrypt_cookies(tampered, "correct horse") is None
    assert decrypt_cookies(dict(blob, n=2 ** 30), "correct horse") is None
    assert decrypt_cookies({"junk": True}, "correct horse") is None


def make_device(tmp_path, name, shared, passphrase="", sync_cookies=True, cookies=None, cookies_ts=0.0, extra_settings=None):
    data = tmp_path / name
    data.mkdir()
    settings = {
        "like_delay_ms": 200,
        "updated_at": 1.0,
        "notifications": {"telegram_token": f"tg-{name}"},
        "sync": {"enabled": True, "method": "folder", "folder_path": str(shared), "webdav_password": f"pw-{name}",
                 "sync_cookies": sync_cookies, "cookie_passphrase": passphrase, "auto_sync_interval_s": 3600},
    }
    settings.update(extra_settings or {})
    (data / "settings.json").write_text(json.dumps(settings))
    (data / "favorites.json").write_text(json.dumps({"creator": True}))
    mgr = SyncManager(data_dir=str(data))
    if cookies is not None:
        mgr._write_cookies(cookies, cookies_ts)
    return mgr


def bundle_text(shared):
    return (shared / FolderSyncBackend.BUNDLE_FILENAME).read_text()


@pytest.fixture
def shared(tmp_path):
    d = tmp_path / "shared"
    d.mkdir()
    return d


def test_bundle_never_contains_credentials_or_plaintext_cookies(tmp_path, shared):
    a = make_device(tmp_path, "a", shared, passphrase="pw", cookies=COOKIES, cookies_ts=100.0)
    try:
        ok, _ = a.sync_now()
        assert ok
        text = bundle_text(shared)
        for secret in ("SECRET-SESSION-VALUE", "pw-a", "tg-a", "cookie_passphrase"):
            assert secret not in text
        data = json.loads(text)
        assert data["cookies"] == [] and data["cookies_encrypted"]
    finally:
        a.stop()


def test_cookies_reach_device_with_same_passphrase_only(tmp_path, shared):
    a = make_device(tmp_path, "a", shared, passphrase="pw", cookies=COOKIES, cookies_ts=100.0)
    b = make_device(tmp_path, "b", shared, passphrase="pw")
    c = make_device(tmp_path, "c", shared, passphrase="different")
    try:
        assert a.sync_now()[0]
        blob_before = json.loads(bundle_text(shared))["cookies_encrypted"]

        ok, msg = c.sync_now()
        assert ok and "passphrase differs" in msg
        assert c._read_cookies()[0] == []
        assert json.loads(bundle_text(shared))["cookies_encrypted"] == blob_before

        assert b.sync_now()[0]
        assert b._read_cookies() == (COOKIES, 100.0)
        # b keeps its own credentials after applying synced settings
        assert b._read_settings()["sync"]["webdav_password"] == "pw-b"
        assert b._read_settings()["notifications"]["telegram_token"] == "tg-b"
    finally:
        for m in (a, b, c):
            m.stop()


def test_no_passphrase_or_cookie_sync_off_keeps_cookies_local(tmp_path, shared):
    a = make_device(tmp_path, "a", shared, passphrase="", cookies=COOKIES, cookies_ts=100.0)
    b = make_device(tmp_path, "b", shared, passphrase="pw", sync_cookies=False, cookies=COOKIES, cookies_ts=200.0)
    try:
        ok, msg = a.sync_now()
        assert ok and "set a cookie passphrase" in msg
        assert b.sync_now()[0]
        data = json.loads(bundle_text(shared))
        assert data["cookies"] == [] and not data["cookies_encrypted"]
        assert "SECRET-SESSION-VALUE" not in bundle_text(shared)
    finally:
        a.stop()
        b.stop()


def test_legacy_bundle_with_secrets_is_rewritten(tmp_path, shared):
    legacy = {
        "version": 1, "timestamp": 50.0, "device_name": "old",
        "settings": {"like_delay_ms": 200, "updated_at": 1.0, "sync": {"webdav_password": "LEAKED-PW"}},
        "favorites": {"creator": {"tapper_enabled": True, "is_muted": True, "updated_at": 1.0}},
        "tombstones": {}, "cookies": COOKIES, "cookies_updated_at": 10.0, "sessions": [],
    }
    (shared / FolderSyncBackend.BUNDLE_FILENAME).write_text(json.dumps(legacy))
    a = make_device(tmp_path, "a", shared, passphrase="pw")
    try:
        assert a.sync_now()[0]
        text = bundle_text(shared)
        assert "LEAKED-PW" not in text and "SECRET-SESSION-VALUE" not in text
        assert decrypt_cookies(json.loads(text)["cookies_encrypted"], "pw") == COOKIES
        assert a._read_cookies()[0] == COOKIES
    finally:
        a.stop()


def test_sign_out_propagates_to_other_devices(tmp_path, shared):
    a = make_device(tmp_path, "a", shared, passphrase="pw", cookies=COOKIES, cookies_ts=100.0)
    b = make_device(tmp_path, "b", shared, passphrase="pw")
    try:
        assert a.sync_now()[0]
        assert b.sync_now()[0]
        assert b._read_cookies()[0] == COOKIES

        a._write_cookies([], 200.0)  # sign out on device A
        assert a.sync_now()[0]
        assert b.sync_now()[0]
        assert b._read_cookies() == ([], 200.0)
    finally:
        a.stop()
        b.stop()
