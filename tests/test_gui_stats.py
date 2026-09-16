import json
import time
from types import SimpleNamespace
from unittest import mock

import pytest

pytest.importorskip("PyQt6.QtWidgets")
app = pytest.importorskip("tiktok_live_auto_liker_tapper")

from stats_manager import TapperStatsProcessor  # noqa: E402


class Label:
    def __init__(self):
        self.text, self.tip, self.css = None, None, None

    def setText(self, t):
        self.text = t

    def setToolTip(self, t):
        self.tip = t

    def setStyleSheet(self, css):
        self.css = css


def fake_tab(background=False):
    titles = SimpleNamespace(last=None)
    tab = SimpleNamespace(
        STANDARD_MILESTONES=app.LiveTab.STANDARD_MILESTONES, _reached_milestones=set(),
        milestone_reached=mock.Mock(), delivery_alert=mock.Mock(), username="demo",
        _tab_opened_at=time.time() - 65, pip_window=None, window=lambda: None,
        _stats=TapperStatsProcessor(), _live_rate=0.0, _last_verified=0, _delivery_state="ok",
        tapper_enabled=True, _is_background=background, settings={"like_delay_ms": 200, "randomization_ms": 5},
        webview=mock.Mock(), lbl_verified=Label(), lbl_rate=Label(), lbl_timer=Label(), lbl_confirmed=Label(),
        tabs_widget=SimpleNamespace(indexOf=lambda w: 0, setTabText=lambda i, t: setattr(titles, "last", t)),
        stats_mgr=mock.Mock(), session_id="sess",
    )
    return tab, titles


def run(tab, **res):
    app.LiveTab._on_tapper_stats_result(tab, {"result": res})


def test_stats_bar_tab_and_session_updates():
    tab, titles = fake_tab()
    run(tab, dispatched=35, verified=30, currentDelay=200, lastAckTime=time.time() * 1000)
    assert "30" in tab.lbl_verified.text
    assert tab.lbl_confirmed.text == "📶 <b>85.7% Confirmed</b> (200ms)"
    assert titles.last == "❤️ LIVE: @demo (❤️ 30)"
    tab.stats_mgr.record_progress.assert_called_with("sess", 30, 35, 0, 0, limit_count=0, limited_seconds=0, like_delay_ms=200)


def test_limited_and_not_counting_states_render():
    tab, titles = fake_tab()
    run(tab, dispatched=60, verified=45, delivery="limited", blockedRemainingMs=95200, blockCount=2, limitedSeconds=12)
    assert "TikTok limit, 1m 36s" in tab.lbl_confirmed.text and "Limit hit 2x" in tab.lbl_confirmed.tip
    assert tab.lbl_confirmed.css == "color: #ffa502;" and titles.last.startswith("⏸️ LIVE")

    run(tab, dispatched=90, verified=45, delivery="unconfirmed", unconfirmedTaps=47)
    assert "Not counting" in tab.lbl_confirmed.text and tab.lbl_confirmed.css == "color: #ff4757;"
    assert titles.last.startswith("⚠️ LIVE")

    run(tab, dispatched=90, verified=60, delivery="ok", currentDelay=220)
    assert tab.lbl_confirmed.css == "color: #2ed573;" and tab.lbl_confirmed.tip == ""

    tab.tapper_enabled = False
    run(tab, dispatched=90, verified=60, delivery="limited", blockedRemainingMs=5000)
    assert "TikTok limit" not in tab.lbl_confirmed.text and titles.last.startswith("LIVE")


def test_alert_signal_emitted_after_threshold():
    tab, _ = fake_tab()
    tab._stats = TapperStatsProcessor(alert_after_s=0)
    run(tab, dispatched=40, verified=0, delivery="unconfirmed", unconfirmedTaps=40)
    tab.delivery_alert.emit.assert_called_once()
    assert tab.delivery_alert.emit.call_args[0][:2] == ("demo", "not_counting")


def test_grid_card_and_pip_show_icon():
    card = SimpleNamespace(lbl_likes=Label())
    app.GridStreamCard.update_likes(card, 1234, "⏸️", "why")
    assert card.lbl_likes.text == "❤️ 1,234 ⏸️" and card.lbl_likes.tip == "why"
    hud = SimpleNamespace(lbl_likes=Label())
    app.PipHudOverlay.update_likes(hud, 99, "⚠️")
    assert hud.lbl_likes.text == "❤️ 99 ⚠️"


def test_notify_delivery_respects_toggle():
    notifier = SimpleNamespace(_send_discord_async=mock.Mock(), _send_telegram_async=mock.Mock())
    settings = {"notifications": {"discord_enabled": True, "discord_url": "https://hook", "notify_not_counting": False}}
    app.WebhookNotifier.notify_delivery(notifier, "demo", "not_counting", "detail", 200, settings)
    notifier._send_discord_async.assert_not_called()
    settings["notifications"]["notify_not_counting"] = True
    app.WebhookNotifier.notify_delivery(notifier, "demo", "not_counting", "detail", 200, settings)
    assert "Likes not counting" in notifier._send_discord_async.call_args.kwargs["title"]


@pytest.mark.parametrize("stored, expected", [
    ({"like_delay_ms": 180, "randomization_ms": 25}, (200, 5)),
    ({"like_delay_ms": 50, "randomization_ms": 50}, (200, 5)),
    ({"like_delay_ms": 260, "randomization_ms": 30}, (260, 30)),
])
def test_settings_migration(tmp_path, stored, expected):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(stored))
    with mock.patch.object(app, "SETTINGS_FILE", str(path)):
        s = app.SettingsManager.load_settings()
    assert (s["like_delay_ms"], s["randomization_ms"]) == expected
