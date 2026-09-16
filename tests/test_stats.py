from stats_manager import (
    LiveRateTracker,
    StatsManager,
    TapperStatsProcessor,
    describe_delivery,
    format_limits,
)

SETTINGS = {"like_delay_ms": 200, "randomization_ms": 5}


def test_rate_readout_is_steady_with_batched_acks():
    tracker = LiveRateTracker()
    start = 1_000_000.0
    tap_interval = 1 / 4.9
    readings, verified, pending, last_ack_ms, next_tap = [], 0, 0, 0, start
    for sec in range(1, 61):
        poll = start + sec
        while next_tap <= poll:
            pending += 1
            if pending == 15:
                verified += 15
                pending = 0
                last_ack_ms = (next_tap + 0.15) * 1000
            next_tap += tap_interval
        dispatched = int((poll - start) * 4.9)
        readings.append(tracker.update(poll, verified, dispatched, last_ack_ms if last_ack_ms / 1000 <= poll else 0))
    assert readings[1] > 4.0  # taps sent stand in before the first ACKs
    assert 4.4 <= min(readings[10:]) and max(readings[10:]) <= 5.4

    for extra in range(1, 13):
        rate = tracker.update(start + 60 + extra, verified, dispatched, last_ack_ms)
    assert rate == 0.0
    assert tracker.update(start + 80, 0, 0, 0) == 0.0  # page reload resets


def test_rate_never_divides_by_back_to_back_polls():
    tracker = LiveRateTracker()
    tracker.update(100.0, 0, 30)
    assert tracker.update(100.00003, 0, 35) <= 5.0


def test_describe_delivery_texts():
    assert describe_delivery({"delivery": "ok"}) == ("ok", "", "")
    state, label, detail = describe_delivery({"delivery": "limited", "blockedRemainingMs": 95200, "blockCount": 2})
    assert state == "limited" and label == "TikTok limit, 1m 36s" and "Limit hit 2x" in detail
    assert "(HTTP 500)" in describe_delivery({"delivery": "rejected", "lastRejectStatus": "HTTP 500"})[2]
    assert "47 taps" in describe_delivery({"delivery": "unconfirmed", "unconfirmedTaps": 47})[2]


def reading(**kw):
    base = {"dispatched": 0, "verified": 0, "delivery": "ok", "blockedRemainingMs": 0}
    base.update(kw)
    return base


def test_processor_alerts_once_per_episode_and_on_recovery():
    proc = TapperStatsProcessor(alert_after_s=180)
    t = 1000.0
    assert proc.process(reading(delivery="unconfirmed", unconfirmedTaps=40), t, True, SETTINGS).alert == ""
    snap = proc.process(reading(delivery="unconfirmed"), t + 179, True, SETTINGS)
    assert snap.alert == "" and snap.not_counting_seconds == 179
    assert proc.process(reading(delivery="limited", blockedRemainingMs=5000), t + 181, True, SETTINGS).alert == "not_counting"
    assert proc.process(reading(delivery="unconfirmed"), t + 240, True, SETTINGS).alert == ""
    assert proc.process(reading(delivery="ok"), t + 241, True, SETTINGS).alert == "recovered"
    assert proc.process(reading(delivery="ok"), t + 242, True, SETTINGS).alert == ""


def test_processor_no_alerts_or_warnings_when_tapper_off():
    proc = TapperStatsProcessor(alert_after_s=10)
    proc.process(reading(delivery="unconfirmed"), 0.0, True, SETTINGS)
    snap = proc.process(reading(delivery="unconfirmed"), 20.0, False, SETTINGS)
    assert snap.delivery == "ok" and snap.alert == ""
    assert proc.process(reading(delivery="ok"), 21.0, True, SETTINGS).alert == ""


def test_watchdog_only_tops_up_when_loop_clearly_behind():
    proc = TapperStatsProcessor()
    proc._last_tick = 0.0
    healthy = proc.process(reading(dispatched=4), 1.0, True, SETTINGS, background=True)
    assert healthy.burst_taps == 0  # 4 of ~5 expected taps is normal jitter

    stalled = proc.process(reading(dispatched=5), 2.0, True, SETTINGS, background=True)
    assert stalled.burst_taps == 3

    blocked = proc.process(reading(dispatched=5, blockedRemainingMs=3000), 3.0, True, SETTINGS, background=True)
    assert blocked.burst_taps == 0

    fg = TapperStatsProcessor()
    fg._last_tick = 0.0
    assert fg.process(reading(dispatched=0), 2.0, True, SETTINGS, background=False).wakeup


def test_processor_parses_all_result_shapes():
    assert TapperStatsProcessor.parse({"result": '{"verified": 3}'}) == {"verified": 3}
    assert TapperStatsProcessor.parse({"result": {"verified": 3}}) == {"verified": 3}
    assert TapperStatsProcessor.parse({"result": "not json"}) is None
    assert TapperStatsProcessor.parse(None) is None


def test_session_records_limits_and_csv(tmp_path):
    mgr = StatsManager(data_dir=str(tmp_path))
    sid = mgr.start_session("creator")
    mgr.record_progress(sid, 100, 110, 15, 0, limit_count=2, limited_seconds=190, like_delay_ms=210)
    mgr.record_progress(sid, 120, 130, 15, 0, limit_count=1, limited_seconds=10, like_delay_ms=220)
    sess = mgr.get_recent_sessions()[0]
    assert (sess["limit_count"], sess["limited_seconds"], sess["like_delay_ms"]) == (2, 190, 220)
    assert format_limits(sess) == "2x, 3m 10s"
    assert format_limits({"limit_count": 0}) == "-"
    mgr.end_session(sid)
    header, row = mgr.export_csv().splitlines()[:2]
    assert header.endswith("TikTok Limits,Limited (s),Like Delay (ms)")
    assert row.endswith(",2,190,220")
