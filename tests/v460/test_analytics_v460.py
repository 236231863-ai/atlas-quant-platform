"""v4.6 P1：用户事件分析系统测试。

覆盖：8事件标准化格式 / 漏斗 / Retention Dashboard / 事件追踪。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.user_analytics import (
    EVENT_NAMES, AnalyticsEvent, AnalyticsTracker, FunnelReport,
    RetentionMetrics, build_funnel, build_retention, track,
)


@pytest.fixture()
def tracker(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    return AnalyticsTracker(str(tmp_path))


def ev(event, day_offset=0, uid="u1", hour=10):
    d = date.today() + timedelta(days=day_offset)
    return AnalyticsEvent(event_name=event, user_id=uid,
                          timestamp=f"{d.isoformat()}T{hour:02d}:00:00",
                          source="desktop", metadata={})


# ---------- 事件格式 ----------
def test_event_fields():
    e = AnalyticsEvent(event_name="app_opened", user_id="u1")
    d = e.to_dict()
    assert d["event_name"] == "app_opened"
    assert d["user_id"] == "u1"
    assert d["source"] == "desktop"
    assert "timestamp" in d
    assert "metadata" in d


def test_event_names_complete():
    expected = {"app_opened", "ticket_saved", "ticket_checked", "reminder_clicked",
                "claim_completed", "report_viewed", "budget_viewed", "export_clicked",
                "premium_view", "premium_click",
                "onboarding_start", "onboarding_complete", "onboarding_drop"}
    assert set(EVENT_NAMES) == expected


# ---------- 追踪 ----------
def test_tracker_record(tracker):
    e = tracker.record("app_opened", metadata={"page": "home"})
    assert e is not None
    assert e.event_name == "app_opened"
    assert tracker.count("app_opened") == 1


def test_tracker_unknown_event(tracker):
    assert tracker.record("hack") is None


def test_tracker_summary(tracker):
    tracker.record("app_opened")
    tracker.record("ticket_saved")
    s = tracker.summary()
    assert s["total"] == 2
    assert s["app_opened"] == 1
    assert s["ticket_saved"] == 1


def test_tracker_all(tracker):
    tracker.record("app_opened")
    evs = tracker.all()
    assert len(evs) == 1
    assert evs[0].event_name == "app_opened"


def test_tracker_clear(tracker):
    tracker.record("app_opened")
    tracker.clear()
    assert tracker.all() == []


@pytest.mark.parametrize("event", list(EVENT_NAMES))
def test_tracker_all_events(tracker, event):
    tracker.record(event)
    assert tracker.count(event) == 1


# ---------- 漏斗 ----------
def test_funnel_empty():
    f = build_funnel([])
    assert f.total_users == 0
    assert len(f.stages) == 5


def test_funnel_full_path():
    events = [ev("app_opened"), ev("ticket_saved"), ev("ticket_checked"),
              ev("claim_completed"), ev("report_viewed")]
    f = build_funnel(events)
    assert f.total_users == 1
    assert all(s.users == 1 for s in f.stages)


def test_funnel_drop():
    # 打开 10 人，只保存 5 人
    events = [ev("app_opened", uid=f"u{i}") for i in range(10)] + \
             [ev("ticket_saved", uid=f"u{i}") for i in range(5)]
    f = build_funnel(events)
    assert f.stages[0].users == 10
    assert f.stages[1].users == 5
    assert f.stages[1].conversion == 0.5
    assert f.stages[1].drop_rate == 0.5


def test_funnel_no_dedup():
    # 同一用户多次保存只算 1 人
    events = [ev("app_opened"), ev("ticket_saved"), ev("ticket_saved")]
    f = build_funnel(events)
    assert f.stages[1].users == 1


def test_funnel_report_text():
    f = build_funnel([])
    assert "用户漏斗" in f.to_text()


def test_funnel_to_dict():
    f = build_funnel([])
    d = f.to_dict()
    assert d["total_users"] == 0
    assert len(d["stages"]) == 5


# ---------- Retention ----------
def test_retention_empty():
    r = build_retention([])
    assert r.active_days == 0


def test_retention_same_day():
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=0)]
    r = build_retention(events)
    assert r.active_days == 1


def test_retention_multiple_days():
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=-1),
              ev("app_opened", day_offset=-3)]
    r = build_retention(events)
    assert r.active_days == 3


def test_retention_d1():
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=1)]
    r = build_retention(events)
    assert r.d1 > 0


def test_retention_d7_absent():
    events = [ev("app_opened", day_offset=0)]
    r = build_retention(events)
    assert r.d7 == 0.0


def test_retention_to_dict():
    r = build_retention([])
    d = r.to_dict()
    assert "d1" in d and "d3" in d and "d7" in d


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 5, 10])
def test_funnel_matrix(tracker, n):
    for i in range(n):
        tracker.record("app_opened")
        tracker.record("ticket_saved")
    f = build_funnel()
    assert f.stages[0].users == min(n, 1)  # 同 user 去重


@pytest.mark.parametrize("seed", range(10))
def test_funnel_random(seed):
    import random
    random.seed(seed)
    events = []
    for i in range(random.randint(1, 15)):
        uid = f"u{random.randint(0, 4)}"
        stage = random.choice(["app_opened", "ticket_saved", "ticket_checked",
                               "claim_completed", "report_viewed"])
        events.append(ev(stage, uid=uid))
    f = build_funnel(events)
    assert f.total_users == len({e.user_id for e in events
                                 if e.event_name == "app_opened"})


@pytest.mark.parametrize("seed", range(10))
def test_retention_random(seed):
    import random
    random.seed(seed)
    events = [ev("app_opened", day_offset=-random.randint(0, 7),
                 uid=f"u{random.randint(0, 3)}") for _ in range(random.randint(1, 30))]
    r = build_retention(events)
    assert r.active_days >= 1
    assert 0.0 <= r.d1 <= 1.0
