"""v4.6 大规模矩阵 2：reminder/claim-summary/onboarding 深度矩阵。"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from engine.draw_monitor.reminder_schedule import ReminderScheduler
from engine.claim_center import ClaimCenter
from engine.user_analytics import AnalyticsTracker


def mk_ticket(tid, draw_date, front=None, back=None, lottery="dlt", claimed=False):
    return {"ticket_id": tid, "lottery": lottery,
            "front": front or [1, 2, 3, 4, 5], "back": back or [1, 2],
            "buy_date": "2026-07-31", "draw_date": draw_date,
            "cost": 2.0, "claimed": claimed}


# ---------- reminder 矩阵 ----------
DRAW_DAY = datetime(2026, 8, 5)  # 周三（大乐透开奖日）


@pytest.mark.parametrize("hour,expect", [
    (0, "pre_24h"), (5, "pre_24h"), (10, "pre_24h"), (15, "pre_24h"),
    (17, "pre_3h"), (18, "pre_3h"), (19, "pre_3h"),
    (20, "after_draw"), (21, "after_draw"), (23, "after_draw"),
])
def test_reminder_by_hour(hour, expect):
    plans = ReminderScheduler.build_plan("dlt", DRAW_DAY.replace(hour=hour))
    kinds = {p.kind for p in plans}
    assert expect in kinds


@pytest.mark.parametrize("day_offset", range(-2, 3))
def test_reminder_by_day(day_offset):
    d = DRAW_DAY + timedelta(days=day_offset)
    plans = ReminderScheduler.build_plan("dlt", d.replace(hour=10))
    assert isinstance(plans, list)


@pytest.mark.parametrize("i", range(20))
def test_reminder_dedup(tmp_path, i):
    assert ReminderScheduler.already_sent("dlt", "pre_24h", str(tmp_path)) is False
    ReminderScheduler._mark_sent("dlt:pre_24h", str(tmp_path))
    assert ReminderScheduler.already_sent("dlt", "pre_24h", str(tmp_path)) is True


# ---------- claim summary 矩阵 ----------
TODAY = date.today().isoformat()
FUTURE = (date.today() + timedelta(days=1)).isoformat()
PAST = (date.today() - timedelta(days=1)).isoformat()


@pytest.mark.parametrize("status,draw_date,claimed", [
    ("waiting_draw", FUTURE, False),
    ("settled_unviewed", PAST, False),
    ("claimed", PAST, True),
])
def test_claim_status_matrix(status, draw_date, claimed):
    t = mk_ticket("T", draw_date, claimed=claimed)
    assert ClaimCenter.status_of(t, TODAY) == status


@pytest.mark.parametrize("n", range(10))
def test_claim_build_items(n):
    tickets = [mk_ticket(f"T{i}", PAST) for i in range(n)]
    items = ClaimCenter.build_items(tickets)
    assert len(items) == n
    assert all(it.status == "settled_unviewed" for it in items)


@pytest.mark.parametrize("n_wait,n_past", [
    (0, 0), (1, 0), (0, 1), (2, 3), (5, 5), (3, 2),
])
def test_claim_pending_matrix(n_wait, n_past):
    tickets = [mk_ticket(f"W{i}", FUTURE) for i in range(n_wait)] + \
              [mk_ticket(f"P{i}", PAST) for i in range(n_past)]
    pending = ClaimCenter.pending_list(tickets)
    assert len(pending) == n_past


@pytest.mark.parametrize("i", range(15))
def test_claim_pending_text(i):
    tickets = [mk_ticket(f"T{j}", PAST if j % 2 else FUTURE) for j in range(i)]
    text = ClaimCenter.pending_text(tickets)
    assert "待兑奖" in text


# ---------- analytics 追踪矩阵 ----------
@pytest.mark.parametrize("event", ["ticket_checked", "reminder_clicked", "budget_viewed", "export_clicked"])
def test_analytics_specific(ticket_storage, event):
    AnalyticsTracker().clear()
    AnalyticsTracker().record(event, source="worker")
    assert AnalyticsTracker().count(event) == 1
    assert AnalyticsTracker().recent(event, 1)[0].source == "worker"


@pytest.mark.parametrize("n", range(15))
def test_analytics_multi_event(ticket_storage, n):
    AnalyticsTracker().clear()
    for i in range(n):
        AnalyticsTracker().record("app_opened")
        AnalyticsTracker().record("ticket_saved")
    s = AnalyticsTracker().summary()
    assert s["app_opened"] == n
    assert s["ticket_saved"] == n
    assert s["total"] == n * 2


# ---------- 综合 ----------
@pytest.mark.parametrize("i", range(15))
def test_reminder_schedule_stable(tmp_path, i):
    due = ReminderScheduler.due_reminders("dlt", DRAW_DAY.replace(hour=10), str(tmp_path))
    ReminderScheduler.mark_reminders_sent(due, str(tmp_path))
    assert ReminderScheduler._load_sent(str(tmp_path))
