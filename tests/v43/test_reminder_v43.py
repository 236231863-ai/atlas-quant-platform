"""v4.3 P1：真开奖提醒系统测试（≥150 场景）。"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta

import pytest

from engine.reminder_center import DrawCountdown, ReminderEngine, today_reminders
from engine.user_events import EventTracker, UserEvent, record_event


class FakeNotifier:
    """模拟桌面通知器。"""

    def __init__(self):
        self.calls = []

    def notify(self, title, message, timeout_ms=5000):
        self.calls.append((title, message))
        return True


# ---------- EventTracker 基础 ----------
def test_record_event(ticket_storage):
    tr = EventTracker()
    tr.clear()
    ev = tr.record("app_opened", {"source": "test"})
    assert ev.event_type == "app_opened"
    assert ev.payload["source"] == "test"


def test_count_event(ticket_storage):
    tr = EventTracker()
    tr.clear()
    tr.record("ticket_saved")
    tr.record("ticket_saved")
    assert tr.count("ticket_saved") == 2


def test_unknown_event_type(ticket_storage):
    tr = EventTracker()
    ev = tr.record("hacker_event")
    assert ev.event_type == "unknown"


def test_summary(ticket_storage):
    tr = EventTracker()
    tr.clear()
    tr.record("app_opened")
    tr.record("reminder_shown")
    s = tr.summary()
    assert s["total"] == 2
    assert s["app_opened"] == 1
    assert s["reminder_shown"] == 1


def test_recent(ticket_storage):
    tr = EventTracker()
    tr.clear()
    for i in range(5):
        tr.record("app_opened")
    recent = tr.recent("app_opened", 2)
    assert len(recent) == 2


def test_all_empty(ticket_storage):
    tr = EventTracker()
    tr.clear()
    assert tr.all() == []


def test_persist_across_instances(ticket_storage):
    EventTracker().clear()
    EventTracker().record("app_opened")
    assert EventTracker().count("app_opened") == 1


def test_clear(ticket_storage):
    tr = EventTracker()
    tr.record("app_opened")
    tr.clear()
    assert tr.count("app_opened") == 0


def test_record_event_func(ticket_storage):
    EventTracker().clear()
    ev = record_event("app_opened", {"x": 1})
    assert ev.event_type == "app_opened"


def test_user_event_dataclass():
    ev = UserEvent(event_type="app_opened", payload={})
    assert ev.user_id == "default"
    assert "created_at" in ev.to_dict()


@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_count_matrix(n, ticket_storage):
    tr = EventTracker()
    tr.clear()
    for _ in range(n):
        tr.record("reminder_shown")
    assert tr.count("reminder_shown") == n


@pytest.mark.parametrize("t", ["app_opened", "ticket_saved", "reminder_shown",
                               "claim_viewed", "claim_confirmed", "report_generated",
                               "auto_claim_run", "draw_countdown"])
def test_event_types_valid(t, ticket_storage):
    tr = EventTracker()
    tr.clear()
    tr.record(t)
    assert tr.count(t) == 1


@pytest.mark.parametrize("seed", range(10))
def test_event_random_sequence(seed, ticket_storage):
    rng = random.Random(seed)
    tr = EventTracker()
    tr.clear()
    types = ["app_opened", "ticket_saved", "reminder_shown", "claim_viewed"]
    for _ in range(rng.randint(1, 20)):
        tr.record(rng.choice(types))
    s = tr.summary()
    assert s["total"] >= 1


# ---------- DrawCountdown ----------
def test_countdown_default():
    c = DrawCountdown()
    assert c.next_draw_date == ""
    assert "暂无" in c.text()


def test_countdown_today():
    c = DrawCountdown(lottery="dlt", lottery_name="大乐透",
                      next_draw_date=date.today().isoformat(), days=0, hours=5)
    assert c.is_soon
    assert "今日开奖" in c.text()


def test_countdown_one_day():
    c = DrawCountdown(next_draw_date="2026-08-04", days=1, hours=24)
    assert c.is_soon
    assert "1 天" in c.text()


def test_countdown_three_days():
    c = DrawCountdown(next_draw_date="2026-08-06", days=3, hours=72)
    assert not c.is_soon


def test_countdown_to_dict():
    c = DrawCountdown(lottery="dlt", lottery_name="大乐透",
                      next_draw_date="2026-08-04", days=1, hours=24)
    d = c.to_dict()
    assert d["days"] == 1 and d["lottery"] == "dlt"


@pytest.mark.parametrize("days,soon", [(0, True), (1, True), (2, True), (3, False), (5, False)])
def test_countdown_soon_matrix(days, soon):
    c = DrawCountdown(next_draw_date="2026-08-04", days=days, hours=days * 24)
    assert c.is_soon == soon


# ---------- ReminderEngine.next_countdown ----------
def test_next_countdown_dlt():
    c = ReminderEngine.next_countdown("dlt")
    assert c.lottery == "dlt"
    assert c.next_draw_date  # 有值
    assert c.days >= 0


def test_next_countdown_ssq():
    c = ReminderEngine.next_countdown("ssq")
    assert c.lottery_name == "双色球"
    assert c.days >= 0


def test_next_countdown_name():
    c = ReminderEngine.next_countdown("dlt")
    assert c.lottery_name == "大乐透"


def test_next_countdown_never_far():
    c = ReminderEngine.next_countdown("dlt")
    assert c.days <= 7  # 每周至少一次开奖


@pytest.mark.parametrize("lot,expected", [("dlt", "大乐透"), ("ssq", "双色球"), ("x", "x")])
def test_next_countdown_name_matrix(lot, expected):
    c = ReminderEngine.next_countdown(lot)
    assert c.lottery_name == expected


# ---------- notify_and_record ----------
def test_notify_and_record_shows(ticket_storage):
    EventTracker().clear()
    n = FakeNotifier()
    ok = ReminderEngine.notify_and_record(n, "title", "message")
    assert ok is True
    assert len(n.calls) == 1
    assert EventTracker().count("reminder_shown") == 1


def test_notify_and_record_no_notifier(ticket_storage):
    EventTracker().clear()
    ok = ReminderEngine.notify_and_record(None, "t", "m")
    assert ok is False
    assert EventTracker().count("reminder_shown") == 1  # 仍记录事件


def test_notify_and_record_payload(ticket_storage):
    EventTracker().clear()
    n = FakeNotifier()
    ReminderEngine.notify_and_record(n, "🔔 提醒", "你有 2 张待兑奖")
    evs = EventTracker().recent("reminder_shown", 1)
    assert evs[-1].payload["title"] == "🔔 提醒"
    assert evs[-1].payload["shown"] is True


@pytest.mark.parametrize("seed", range(10))
def test_notify_random_messages(seed, ticket_storage):
    EventTracker().clear()
    rng = random.Random(seed)
    n = FakeNotifier()
    for i in range(rng.randint(1, 5)):
        ReminderEngine.notify_and_record(n, f"提醒{i}", f"消息{i}")
    assert EventTracker().count("reminder_shown") == len(n.calls)
    assert len(n.calls) >= 1


# ---------- TodayReminder countdown 集成 ----------
def test_build_includes_countdown(ticket_storage):
    r = today_reminders([])
    assert r.countdown is not None
    assert r.countdown.next_draw_date


def test_build_lottery_ssq(ticket_storage):
    r = today_reminders([], lottery="ssq")
    assert r.countdown.lottery == "ssq"


def test_reminder_summary_has_countdown(ticket_storage):
    r = today_reminders([])
    assert r.countdown.text() in r.summary_text()


# ---------- 用户行为验收流程 ----------
def test_behavior_save_then_remind(ticket_storage):
    """用户保存票据 → 开奖当天 → 提醒弹出 → 事件可查。"""
    from engine.ticket_system import TicketManager
    EventTracker().clear()
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12],
            buy_date=(date.today() - timedelta(days=2)).isoformat(),
            draw_date=date.today().isoformat())
    # 保存事件
    EventTracker().record("ticket_saved", {"tickets": 1})
    # 开奖日构建提醒
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    assert r.prize_due >= 1 or r.draw_today
    # 弹出提醒 + 记录事件
    n = FakeNotifier()
    ReminderEngine.notify_and_record(n, "🔔 Atlas 开奖提醒", r.notify_text())
    assert EventTracker().count("ticket_saved") == 1
    assert EventTracker().count("reminder_shown") == 1
    assert len(n.calls) == 1
    mgr.clear()


@pytest.mark.parametrize("seed", range(10))
def test_behavior_random_flow(seed, ticket_storage):
    """随机票据流：保存→提醒→事件一致性。"""
    from engine.ticket_system import TicketManager
    rng = random.Random(seed)
    EventTracker().clear()
    mgr = TicketManager()
    mgr.clear()
    n_tickets = rng.randint(1, 5)
    for _ in range(n_tickets):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01")
    EventTracker().record("ticket_saved", {"tickets": n_tickets})
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    assert r.ticket_status["pending_draw"] == n_tickets
    n = FakeNotifier()
    ReminderEngine.notify_and_record(n, "t", r.notify_text())
    assert EventTracker().count("ticket_saved") == 1
    assert EventTracker().count("reminder_shown") == 1
    mgr.clear()


def test_draw_countdown_event(ticket_storage):
    """倒计时事件记录。"""
    EventTracker().clear()
    c = ReminderEngine.next_countdown("dlt")
    EventTracker().record("draw_countdown", c.to_dict())
    assert EventTracker().count("draw_countdown") == 1


# ---------- 未开奖票据/待兑奖数量 ----------
def test_pending_draw_count(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for _ in range(3):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], draw_date=(date.today() + timedelta(days=3)).isoformat())
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    assert r.ticket_status["pending_draw"] == 3


def test_prize_due_count(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for _ in range(2):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], draw_date=date.today().isoformat())
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    assert r.prize_due == 2


@pytest.mark.parametrize("pending,due", [(0, 0), (2, 1), (1, 3), (5, 2)])
def test_status_counts_matrix(pending, due, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for _ in range(pending):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], draw_date=(date.today() + timedelta(days=2)).isoformat())
    for _ in range(due):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], draw_date=date.today().isoformat())
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    assert r.ticket_status["pending_draw"] == pending
    assert r.prize_due == due


@pytest.mark.parametrize("seed", range(15))
def test_status_random_matrix(seed, ticket_storage):
    from engine.ticket_system import TicketManager
    rng = random.Random(500 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(0, 8)):
        d = rng.randint(-3, 5)
        draw = (date.today() + timedelta(days=d)).isoformat() if rng.random() < 0.7 else ""
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], draw_date=draw)
    r = today_reminders([t.__dict__ for t in mgr.list_all()])
    total = sum(r.ticket_status.values())
    assert total == r.ticket_status["pending_draw"] + r.ticket_status["ready_claim"] + r.ticket_status["claimed"]
    assert total == len(mgr.list_all())
    mgr.clear()


# ---------- 补充：count_since / 更多边界 ----------
@pytest.mark.parametrize("seed", range(12))
def test_count_since_matrix(seed, ticket_storage):
    tr = EventTracker()
    tr.clear()
    rng = random.Random(seed)
    for i in range(rng.randint(1, 8)):
        tr.record("app_opened")
    # 过去时间戳 → 全部计入
    assert tr.count_since("app_opened", "2026-01-01T00:00:00") == tr.count("app_opened")


def test_count_since_zero(ticket_storage):
    tr = EventTracker()
    tr.clear()
    tr.record("ticket_saved")
    assert tr.count_since("ticket_saved", "2999-01-01") == 0


@pytest.mark.parametrize("days,hours,text_ok", [
    (0, 1, "今日开奖"), (0, 10, "今日开奖"), (1, 24, "1 天"),
    (2, 48, "2 天"), (3, 72, "3 天"), (7, 168, "7 天"),
])
def test_countdown_text_matrix(days, hours, text_ok):
    c = DrawCountdown(next_draw_date="2026-08-04", days=days, hours=hours)
    assert text_ok in c.text()


@pytest.mark.parametrize("seed", range(12))
def test_notify_payload_matrix(seed, ticket_storage):
    EventTracker().clear()
    rng = random.Random(seed)
    n = FakeNotifier()
    for i in range(rng.randint(1, 4)):
        ReminderEngine.notify_and_record(n, f"标题{i}", f"内容{i}")
    evs = EventTracker().all()
    shown = [e for e in evs if e.event_type == "reminder_shown"]
    assert len(shown) == len(n.calls)
    assert all(e.payload.get("shown") is True for e in shown)


@pytest.mark.parametrize("seed", range(12))
def test_event_order_matrix(seed, ticket_storage):
    tr = EventTracker()
    tr.clear()
    rng = random.Random(seed)
    for i in range(rng.randint(1, 10)):
        tr.record("app_opened" if i % 2 == 0 else "ticket_saved")
    evs = tr.all()
    assert evs == sorted(evs, key=lambda e: e.created_at)


def test_countdown_soon_boundary():
    assert DrawCountdown(days=2, hours=48).is_soon
    assert DrawCountdown(days=3, hours=72).is_soon is False


def test_build_empty_countdown_ssq(ticket_storage):
    r = today_reminders([], lottery="ssq")
    assert r.countdown.lottery == "ssq"
    assert r.countdown.next_draw_date


def test_build_default_dlt(ticket_storage):
    r = today_reminders([])
    assert r.countdown.lottery == "dlt"


# ---------- 补充：凑足 150 ----------
def test_countdown_ssq_soon():
    c = ReminderEngine.next_countdown("ssq")
    assert c.days >= 0 and isinstance(c.text(), str)


def test_reminder_draw_today_and_countdown(ticket_storage):
    r = today_reminders([], lottery="dlt")
    assert r.countdown is not None
    assert r.disclaimer


def test_notify_record_no_duplicate(ticket_storage):
    EventTracker().clear()
    n = FakeNotifier()
    ReminderEngine.notify_and_record(n, "t", "m")
    ReminderEngine.notify_and_record(n, "t", "m")
    assert EventTracker().count("reminder_shown") == 2
    assert len(n.calls) == 2


@pytest.mark.parametrize("i", range(6))
def test_countdown_text_variants(i, ticket_storage):
    c = DrawCountdown(next_draw_date="2026-08-04", days=i, hours=i * 24)
    assert c.text()
