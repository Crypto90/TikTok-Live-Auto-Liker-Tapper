import json
import time
from types import SimpleNamespace
from unittest import mock

from stats_manager import TapperStatsProcessor
from sync_manager import SyncManager

SECRETS = {"webdav_password": "dav-pw", "rest_api_key": "rest-key", "cookie_passphrase": "cookie-pw"}


def fake_runner(headless_module, tmp_path):
    settings = {
        "like_delay_ms": 200,
        "notifications": {"telegram_token": "tg-token", "notify_live": True},
        "sync": dict(SECRETS, enabled=False, method="webdav", webdav_url="https://dav"),
    }
    (tmp_path / "settings.json").write_text(json.dumps(settings))
    runner = SimpleNamespace(
        sync_mgr=SyncManager(data_dir=str(tmp_path)), settings=settings, active_streams={}, log=lambda msg: None,
        SYNC_CONFIG_KEYS=headless_module.HeadlessServerManager.SYNC_CONFIG_KEYS,
        SECRET_SYNC_KEYS=headless_module.HeadlessServerManager.SECRET_SYNC_KEYS,
    )
    runner._with_saved_secrets = lambda cfg: headless_module.HeadlessServerManager._with_saved_secrets(runner, cfg)
    return runner


def test_sync_config_never_returns_secrets(headless_module, tmp_path):
    runner = fake_runner(headless_module, tmp_path)
    cfg = headless_module.HeadlessServerManager.get_sync_config(runner)
    text = json.dumps(cfg)
    for secret in SECRETS.values():
        assert secret not in text
    assert cfg["webdav_password_set"] and cfg["rest_api_key_set"] and cfg["cookie_passphrase_set"]


def test_blank_secret_keeps_saved_value_and_unknown_keys_dropped(headless_module, tmp_path):
    runner = fake_runner(headless_module, tmp_path)
    headless_module.HeadlessServerManager.save_sync_config(runner, {
        "enabled": False, "method": "webdav", "webdav_url": "https://new", "webdav_password": "",
        "rest_api_key": "new-key", "cookie_passphrase": "", "evil": "x",
    })
    saved = runner.sync_mgr._read_settings()["sync"]
    assert saved["webdav_password"] == "dav-pw" and saved["cookie_passphrase"] == "cookie-pw"
    assert saved["rest_api_key"] == "new-key" and saved["webdav_url"] == "https://new"
    assert "evil" not in saved


def test_settings_endpoint_redacts_and_update_is_allow_listed(headless_module, tmp_path, monkeypatch):
    runner = fake_runner(headless_module, tmp_path)
    public = headless_module.HeadlessServerManager.get_settings(runner)
    assert "sync" not in public and "telegram_token" not in json.dumps(public)

    monkeypatch.setattr(headless_module, "DATA_DIR", str(tmp_path))
    runner.sync_mgr.record_local_change = lambda: None
    headless_module.HeadlessServerManager.update_settings(runner, {
        "like_delay_ms": 50, "randomization_ms": 500, "adaptive_rate": 0, "sync": {"enabled": True, "webdav_url": "https://evil"},
    })
    assert runner.settings["like_delay_ms"] == 200 and runner.settings["randomization_ms"] == 100
    assert runner.settings["adaptive_rate"] is False
    assert runner.settings["sync"]["webdav_url"] == "https://dav"


def test_headless_stats_callback_updates_fields_and_logs_alert(headless_module):
    logs = []
    parent = SimpleNamespace(log=logs.append)
    tab = SimpleNamespace(
        _stats=TapperStatsProcessor(alert_after_s=0), tapper_enabled=True, settings={"like_delay_ms": 200},
        webview=mock.Mock(), stats_mgr=mock.Mock(), session_id="s1", username="demo", parent=lambda: parent,
    )
    headless_module.HeadlessStreamTab._on_tapper_stats_result(
        tab, {"result": {"dispatched": 50, "verified": 15, "delivery": "unconfirmed", "unconfirmedTaps": 35,
                         "blockCount": 1, "limitedSeconds": 7, "lastAckTime": time.time() * 1000}})
    assert (tab.verified_likes, tab.taps_dispatched, tab.delivery) == (15, 50, "unconfirmed")
    assert logs and logs[0].startswith("[NOT COUNTING] @demo")
    tab.stats_mgr.record_progress.assert_called_with("s1", 15, 50, 0, 0, limit_count=1, limited_seconds=7, like_delay_ms=200)


def test_cli_accepts_host_token_and_headless_flag(headless_module, monkeypatch):
    captured = {}

    class Stop(Exception):
        pass

    def fake_manager(**kwargs):
        captured.update(kwargs)
        raise Stop

    monkeypatch.setattr(headless_module, "HeadlessServerManager", fake_manager)
    monkeypatch.setattr(headless_module, "QApplication", lambda argv: None)
    monkeypatch.setattr("sys.argv", ["app", "--headless", "--host", "0.0.0.0", "--token", "abc", "--port", "9000"])
    try:
        headless_module.main()
    except Stop:
        pass
    assert captured == {"port": 9000, "enable_web": True, "host": "0.0.0.0", "access_token": "abc"}
