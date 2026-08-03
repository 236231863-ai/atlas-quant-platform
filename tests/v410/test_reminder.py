"""v4.1 阶段2：开奖提醒中心测试。"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.reminder_center import ReminderEngine, TodayReminder, today_reminders


def _tk(front, back, buy=None, draw=None):
    return {"front": front, "back": back,
            "buy_date": buy or (date.today() - timedelta(days=3)).isoformat(),
            "draw_date": draw or ""}


TODAY = date.today().isoformat()


# ---------- 今日开奖 ----------
def test_draw_today():
    r = ReminderEngine._draw_today()
    from engine.ticket_system.schedule import LotterySchedule
    assert ("大乐透" in r) == LotterySchedule.is_draw_day("dlt", TODAY)
    assert ("双色球" in r) == LotterySchedule.is_draw_day("ssq", TODAY)


def test_reminder_draw_today():
    r = today_reminders([])
    assert isinstance(r.draw_today, list)


@pytest.mark.parametrize("i", range(10))
def test_draw_today_valid(i):
    r = ReminderEngine._draw_today()
    for name in r:
        assert name in ("大乐透", "双色球")


# ---------- 可兑奖/未兑奖 ----------
def test_prize_due_today():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=TODAY)
    r = today_reminders([t])
    assert r.prize_due == 1


def test_unclaimed_past():
    t = _tk([1, 2, 3, 4, 5], [6, 7], draw=(date.today() - timedelta(days=2)).isoformat())
    r = today_reminders([t])
    assert r.unclaimed >= 1


def test_no_ticket_no_reminder():
    r = today_reminders([])
    assert r.prize_due == 0
    assert r.unclaimed == 0


def test_mixed():
    t1 = _tk([1, 2, 3, 4, 5], [6, 7], draw=TODAY)
    t2 = _tk([5, 6, 7, 8, 9], [1, 2], draw=(date.today() - timedelta(days=1)).isoformat())
    r = today_reminders([t1, t2])
    assert r.prize_due == 1
    assert r.unclaimed == 1


@pytest.mark.parametrize("n", [1, 3, 5, 8])
def test_prize_due_count(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7], draw=TODAY) for _ in range(n)]
    r = today_reminders(tickets)
    assert r.prize_due == n


# ---------- 追号提醒 ----------
def test_chase_reminder():
    tickets = [
        _tk([10, 11, 18, 22, 35], [6, 12], buy=(date.today() - timedelta(days=7)).isoformat()),
        _tk([10, 11, 18, 22, 35], [6, 12], buy=(date.today() - timedelta(days=14)).isoformat()),
    ]
    r = today_reminders(tickets)
    assert len(r.chase_notes) == 1
    assert r.chase_notes[0]["streak"] == 2


def test_no_chase():
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7]), _tk([6, 7, 8, 9, 10], [1, 2])]
    r = today_reminders(tickets)
    assert r.chase_notes == []


@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_chase_streak(n):
    tickets = [_tk([10, 11, 18, 22, 35], [6, 12],
                   buy=(date.today() - timedelta(days=7 * i)).isoformat()) for i in range(n)]
    r = today_reminders(tickets)
    assert len(r.chase_notes) == 1
    assert r.chase_notes[0]["streak"] == n


# ---------- 下次开奖 ----------
def test_next_draws():
    r = today_reminders([])
    assert len(r.next_draws) >= 1
    for nd in r.next_draws[:3]:
        assert nd["lottery_name"] in ("大乐透", "双色球")
        assert nd["date"] > TODAY


@pytest.mark.parametrize("i", range(10))
def test_next_draws_ascending(i):
    r = today_reminders([])
    dates = [nd["date"] for nd in r.next_draws]
    assert dates == sorted(dates)


# ---------- 报告结构 ----------
def test_reminder_type():
    r = today_reminders([])
    assert isinstance(r, TodayReminder)


@pytest.mark.parametrize("f", ["today", "draw_today", "prize_due",
                               "unclaimed", "chase_notes", "next_draws"])
def test_reminder_fields(f):
    r = today_reminders([])
    assert hasattr(r, f)


@pytest.mark.parametrize("f", ["today", "draw_today", "prize_due",
                               "unclaimed", "chase_notes", "next_draws"])
def test_reminder_dict_keys(f):
    r = today_reminders([])
    assert f in r.to_dict()


def test_summary_text_fields():
    r = today_reminders([])
    t = r.summary_text()
    assert "今日提醒" in t
    assert "随机性" in t


def test_has_anything():
    r = today_reminders([])
    assert isinstance(r.has_anything, bool)


# ---------- 免责声明 ----------
def test_disclaimer():
    r = today_reminders([])
    assert "随机性" in r.disclaimer
    assert "不涉及预测" in r.disclaimer or "预测" not in r.disclaimer


def test_summary_disclaimer():
    r = today_reminders([])
    assert "随机性" in r.summary_text()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_reminder_matrix(seed):
    rng = random.Random(seed)
    tickets = []
    for _ in range(rng.randint(1, 10)):
        f = sorted(rng.sample(range(1, 36), 5))
        b = sorted(rng.sample(range(1, 13), 2))
        d = rng.randint(-30, 5)
        tickets.append(_tk(f, b, draw=(date.today() + timedelta(days=d)).isoformat()))
    r = today_reminders(tickets)
    assert r.prize_due >= 0
    assert r.unclaimed >= 0
    assert 0 <= r.prize_due + r.unclaimed <= len(tickets)


@pytest.mark.parametrize("seed", range(30))
def test_chase_matrix(seed):
    rng = random.Random(1000 + seed)
    combo = (sorted(rng.sample(range(1, 36), 5)), sorted(rng.sample(range(1, 13), 2)))
    tickets = [_tk(combo[0], combo[1],
                   buy=(date.today() - timedelta(days=7 * i)).isoformat())
               for i in range(rng.randint(2, 8))]
    r = today_reminders(tickets)
    assert len(r.chase_notes) == 1
    assert r.chase_notes[0]["streak"] == len(tickets)


@pytest.mark.parametrize("seed", range(20))
def test_reminder_no_crash(seed):
    rng = random.Random(2000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(rng.randint(0, 8))]
    r = today_reminders(tickets)
    assert isinstance(r.summary_text(), str)


@pytest.mark.parametrize("seed", range(20))
def test_reminder_dict_valid(seed):
    r = today_reminders([])
    d = r.to_dict()
    assert isinstance(d["next_draws"], list)
    assert isinstance(d["draw_today"], list)
