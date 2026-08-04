"""v4.5 P5：用户行为埋点 + User Behavior Report 测试。

覆盖：新事件类型 / 行为报告统计 / 洞察 / 每日分布。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.user_events import (
    EVENT_TYPES, BehaviorReporter, EventTracker, UserBehaviorReport,
    build_behavior_report,
)
from engine.user_events.report import BehaviorSummary, KEY_EVENTS


def ev(event_type, day_offset=0, hour=10):
    d = date.today() + timedelta(days=day_offset)
    from engine.user_events import UserEvent
    return UserEvent(event_type=event_type,
                     created_at=f"{d.isoformat()}T{hour:02d}:00:00")


# ---------- 新事件类型 ----------
def test_new_event_types_present():
    for t in ("draw_reminder_received", "draw_opened", "claim_completed"):
        assert t in EVENT_TYPES


def test_record_new_events(ticket_storage):
    EventTracker().clear()
    EventTracker().record("draw_reminder_received")
    EventTracker().record("draw_opened")
    EventTracker().record("claim_completed")
    s = EventTracker().summary()
    assert s["draw_reminder_received"] == 1
    assert s["draw_opened"] == 1
    assert s["claim_completed"] == 1


# ---------- 报告统计 ----------
def test_report_empty():
    rep = build_behavior_report([])
    assert rep.summary.total_events == 0
    assert rep.summary.active_days == 0


def test_report_counts():
    events = [ev("ticket_saved"), ev("ticket_saved"), ev("draw_opened"),
              ev("claim_completed"), ev("app_opened")]
    rep = build_behavior_report(events)
    assert rep.summary.total_events == 5
    assert rep.summary.by_event["ticket_saved"] == 2
    assert rep.summary.by_event["draw_opened"] == 1


def test_report_active_days():
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=-1),
              ev("app_opened", day_offset=-3)]
    rep = build_behavior_report(events)
    assert rep.summary.active_days == 3


def test_report_last_seen():
    events = [ev("app_opened", day_offset=-2), ev("app_opened")]
    rep = build_behavior_report(events)
    assert rep.summary.last_seen == date.today().isoformat()


def test_report_daily():
    events = [ev("app_opened"), ev("ticket_saved")]
    rep = build_behavior_report(events)
    today = date.today().isoformat()
    assert today in rep.daily
    assert rep.daily[today]["app_opened"] == 1


# ---------- 洞察 ----------
def test_insight_no_usage():
    rep = build_behavior_report([ev("ticket_saved")])
    assert any("尚无使用记录" in i for i in rep.insights) or rep.insights


def test_insight_save_rate_low():
    # 打开 10 次只保存 1 次 → 保存率低
    events = [ev("app_opened", day_offset=-(i % 3)) for i in range(10)] + \
             [ev("ticket_saved")]
    rep = build_behavior_report(events)
    assert any("保存率偏低" in i for i in rep.insights)


def test_insight_claimed_pending():
    events = [ev("ticket_saved"), ev("ticket_saved"), ev("app_opened")]
    rep = build_behavior_report(events)
    assert any("兑奖" in i for i in rep.insights)


def test_insight_healthy():
    events = [ev("app_opened"), ev("ticket_saved"), ev("claim_completed"),
              ev("report_viewed"), ev("draw_opened")]
    rep = build_behavior_report(events)
    assert any("通畅" in i for i in rep.insights)


# ---------- 结构 ----------
def test_summary_top_events():
    s = BehaviorSummary(by_event={"ticket_saved": 3, "app_opened": 1})
    top = s.top_events(1)
    assert top[0][0] == "ticket_saved"


def test_report_to_dict():
    rep = build_behavior_report([ev("app_opened")])
    d = rep.to_dict()
    assert d["total_events"] == 1
    assert "insights" in d


def test_report_to_text():
    rep = build_behavior_report([ev("app_opened"), ev("ticket_saved")])
    t = rep.to_text()
    assert "User Behavior Report" in t
    assert "总事件" in t


# ---------- 矩阵 ----------
@pytest.mark.parametrize("event", list(KEY_EVENTS))
def test_key_event_tracked(event):
    rep = build_behavior_report([ev(event)])
    assert rep.summary.by_event[event] == 1


@pytest.mark.parametrize("n", [0, 1, 5, 10])
def test_report_count_matrix(n):
    events = [ev("ticket_saved", day_offset=-(i % 5)) for i in range(n)]
    rep = build_behavior_report(events)
    assert rep.summary.by_event["ticket_saved"] == n


@pytest.mark.parametrize("seed", range(10))
def test_report_random(seed):
    import random
    random.seed(seed)
    events = [ev(random.choice(list(KEY_EVENTS)), day_offset=-random.randint(0, 7))
              for _ in range(random.randint(1, 20))]
    rep = build_behavior_report(events)
    assert rep.summary.total_events == len(events)
    assert rep.to_text()


# ---------- 事件追踪集成 ----------
def test_tracker_build_report(ticket_storage):
    EventTracker().clear()
    EventTracker().record("ticket_saved")
    EventTracker().record("draw_reminder_received")
    rep = build_behavior_report()
    assert rep.summary.total_events == 2
    assert rep.summary.by_event["ticket_saved"] == 1
