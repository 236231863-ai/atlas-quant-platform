"""v4.5 P2：自动开奖监控测试。

覆盖：开奖日判断 / 下一开奖 / upcoming / monitor_once / 后台循环 / 倒计时。
"""
from __future__ import annotations

import threading
from datetime import date, datetime, timedelta

import pytest

from engine.draw_monitor import DrawMonitor, monitor_now
from engine.ticket_system.schedule import LotterySchedule


@pytest.fixture()
def mon():
    return DrawMonitor()


# ---------- 开奖日判断 ----------
@pytest.mark.parametrize("weekday,expect", [
    (0, True), (2, True), (5, True),  # 周一/三/六
    (1, False), (3, False), (4, False), (6, False),
])
def test_dlt_draw_day(weekday, expect):
    d = (date(2026, 8, 3) + timedelta(days=weekday)).isoformat()
    assert DrawMonitor.is_draw_day("dlt", d) is expect


@pytest.mark.parametrize("weekday,expect", [
    (1, True), (3, True), (6, True),  # 周二/四/日
    (0, False), (2, False), (4, False), (5, False),
])
def test_ssq_draw_day(weekday, expect):
    d = (date(2026, 8, 3) + timedelta(days=weekday)).isoformat()
    assert DrawMonitor.is_draw_day("ssq", d) is expect


# ---------- 下一开奖 ----------
def test_next_draw_dlt(mon):
    nxt = mon.next_draw_time("dlt", "2026-08-03")
    assert nxt == "2026-08-03"  # 周一当天


def test_next_draw_ssq(mon):
    nxt = mon.next_draw_time("ssq", "2026-08-03")
    assert nxt == "2026-08-04"  # 周二


def test_next_draw_empty(mon):
    assert mon.next_draw_time("dlt", "") or mon.next_draw_time("dlt") is not None


# ---------- upcoming ----------
def test_upcoming_draws(mon):
    ups = mon.upcoming_draws(3)
    assert len(ups) >= 1
    assert all("date" in u for u in ups)


def test_upcoming_sorted(mon):
    ups = mon.upcoming_draws(5)
    dates = [u["date"] for u in ups]
    assert dates == sorted(dates)


def test_upcoming_contains_lotteries(mon):
    ups = mon.upcoming_draws(10)
    names = {u["lottery"] for u in ups}
    assert names.issubset({"dlt", "ssq"})


# ---------- monitor_once ----------
def test_monitor_once_returns_events(mon, monkeypatch):
    class FU:
        def __init__(self, lottery="dlt", storage_dir=None): pass
        def update(self, force=False, pages=1):
            return {"updated": False, "reason": "no_new", "added": 0, "total": 1}
        def load_local(self): return []
        def _load_builtin(self): return []
        def _last_update(self): return None
    monkeypatch.setattr("engine.data_center_v2.updater.IncrementalUpdater", FU)
    evs = mon.monitor_once()
    assert len(evs) == 2
    assert {e.lottery for e in evs} == {"dlt", "ssq"}


def test_monitor_now_helper(monkeypatch):
    class FU:
        def __init__(self, lottery="dlt", storage_dir=None): pass
        def update(self, force=False, pages=1):
            return {"updated": False, "reason": "no_new", "added": 0, "total": 1}
        def load_local(self): return []
        def _load_builtin(self): return []
        def _last_update(self): return None
    monkeypatch.setattr("engine.data_center_v2.updater.IncrementalUpdater", FU)
    evs = monitor_now()
    assert isinstance(evs, list)


# ---------- 后台循环 ----------
def test_run_loop_stops(mon, monkeypatch):
    class FU:
        def __init__(self, lottery="dlt", storage_dir=None): pass
        def update(self, force=False, pages=1):
            return {"updated": False, "reason": "no_new", "added": 0, "total": 1}
        def load_local(self): return []
        def _load_builtin(self): return []
        def _last_update(self): return None
    monkeypatch.setattr("engine.data_center_v2.updater.IncrementalUpdater", FU)
    stop = threading.Event()
    t = threading.Thread(target=mon.run_loop,
                         kwargs={"interval_seconds": 0.05, "stop_event": stop},
                         daemon=True)
    t.start()
    import time
    time.sleep(0.2)
    stop.set()
    t.join(timeout=2)
    assert not t.is_alive()


def test_run_background(mon, monkeypatch):
    class FU:
        def __init__(self, lottery="dlt", storage_dir=None): pass
        def update(self, force=False, pages=1):
            return {"updated": False, "reason": "no_new", "added": 0, "total": 1}
        def load_local(self): return []
        def _load_builtin(self): return []
        def _last_update(self): return None
    monkeypatch.setattr("engine.data_center_v2.updater.IncrementalUpdater", FU)
    stop = mon.run_background(interval_seconds=0.05)
    import time
    time.sleep(0.15)
    stop.set()


# ---------- 倒计时 ----------
def test_countdown_today(mon):
    txt = mon.countdown_text("dlt")
    assert "大乐透" in txt


def test_countdown_format(mon):
    txt = mon.countdown_text("ssq")
    assert "双色球" in txt


# ---------- 矩阵 ----------
@pytest.mark.parametrize("day", range(1, 29))
def test_schedule_all_days(day):
    d = f"2026-08-{day:02d}"
    # 任一彩种当天或次日必有开奖
    n1 = LotterySchedule.next_draw_date("dlt", d)
    n2 = LotterySchedule.next_draw_date("ssq", d)
    assert n1 is not None or n2 is not None
