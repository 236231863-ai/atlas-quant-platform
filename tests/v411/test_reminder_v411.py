"""v4.1.1 Phase 1：真开奖提醒系统测试（状态机 + 通知 + 100 场景）。"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.reminder_center import ReminderEngine, today_reminders

TODAY = date.today().isoformat()


def _tk(front, back, draw=None, buy=None, claimed=False):
    return {"front": front, "back": back,
            "buy_date": buy or (date.today() - timedelta(days=3)).isoformat(),
            "draw_date": draw or "", "claimed": claimed}


# ---------- 票据状态机 ----------
def test_status_pending_draw():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() + timedelta(days=2)).isoformat())
    s = ReminderEngine.ticket_status([t])
    assert s["pending_draw"] == 1
    assert s["ready_claim"] == 0


def test_status_ready_claim():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=1)).isoformat())
    s = ReminderEngine.ticket_status([t])
    assert s["ready_claim"] == 1


def test_status_claimed():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=1)).isoformat(), claimed=True)
    s = ReminderEngine.ticket_status([t])
    assert s["claimed"] == 1


def test_status_no_draw_is_pending():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw="")
    s = ReminderEngine.ticket_status([t])
    assert s["pending_draw"] == 1


def test_status_empty():
    s = ReminderEngine.ticket_status([])
    assert s == {"pending_draw": 0, "ready_claim": 0, "claimed": 0}


@pytest.mark.parametrize("n", [1, 3, 5, 8])
def test_status_pending_count(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() + timedelta(days=i + 1)).isoformat())
               for i in range(n)]
    s = ReminderEngine.ticket_status(tickets)
    assert s["pending_draw"] == n


@pytest.mark.parametrize("n", [1, 2, 4])
def test_status_ready_count(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=i + 1)).isoformat())
               for i in range(n)]
    s = ReminderEngine.ticket_status(tickets)
    assert s["ready_claim"] == n


def test_status_mixed():
    tickets = [
        _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() + timedelta(days=2)).isoformat()),
        _tk([5, 6, 7, 8, 9], [1, 2], draw=(date.today() - timedelta(days=1)).isoformat()),
        _tk([8, 9, 10, 11, 12], [3, 4], draw=(date.today() - timedelta(days=3)).isoformat(), claimed=True),
    ]
    s = ReminderEngine.ticket_status(tickets)
    assert s == {"pending_draw": 1, "ready_claim": 1, "claimed": 1}


# ---------- 通知文案 ----------
def test_notify_draw_day():
    r = today_reminders([])
    if r.draw_today:
        assert "开奖" in r.notify_text()


def test_notify_prize_due():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=TODAY)
    r = today_reminders([t])
    assert "兑奖" in r.notify_text()


def test_notify_unclaimed():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=2)).isoformat())
    r = today_reminders([t])
    # 开奖日优先；非开奖日时应提示未确认
    if not r.draw_today:
        assert "未确认" in r.notify_text()
    else:
        assert r.notify_text()  # 开奖日提示优先，非空即可


def test_notify_default():
    r = today_reminders([])
    assert r.notify_text()


# ---------- 100 提醒场景 ----------
@pytest.mark.parametrize("seed", range(50))
def test_reminder_scenarios(seed):
    rng = random.Random(seed)
    tickets = []
    n = rng.randint(0, 5)
    for _ in range(n):
        d = rng.randint(-5, 5)
        draw = (date.today() + timedelta(days=d)).isoformat() if rng.random() < 0.7 else ""
        tickets.append(_tk([1, 2, 3, 4, 5], [6, 7], draw=draw,
                           claimed=rng.random() < 0.2))
    r = today_reminders(tickets)
    # 状态机一致性
    total = r.ticket_status["pending_draw"] + r.ticket_status["ready_claim"] + r.ticket_status["claimed"]
    assert total == n
    assert r.notify_text()


@pytest.mark.parametrize("seed", range(50))
def test_reminder_multi_ticket(seed):
    rng = random.Random(1000 + seed)
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   draw=(date.today() - timedelta(days=rng.randint(0, 3))).isoformat())
               for _ in range(rng.randint(1, 10))]
    r = today_reminders(tickets)
    assert r.ticket_status["ready_claim"] + r.ticket_status["claimed"] >= 1
    assert r.prize_due + r.unclaimed >= 1


# ---------- 通知器 ----------
def test_notifier_available():
    from pages.reminder_notifier import ReminderNotifier
    n = ReminderNotifier()
    assert hasattr(n, "notify")
    assert hasattr(n, "show_draw_reminder")


def test_notifier_no_crash():
    from pages.reminder_notifier import ReminderNotifier
    n = ReminderNotifier()
    n.notify("test", "test message")
    n.show_draw_reminder("test")


# ---------- 重复提醒 ----------
def test_repeat_same_tickets():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=1)).isoformat())
    r1 = today_reminders([t])
    r2 = today_reminders([t, t])
    assert r2.unclaimed >= r1.unclaimed


# ---------- 过期开奖 ----------
def test_old_draw():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=10)).isoformat())
    r = today_reminders([t])
    assert r.unclaimed >= 1
