"""v4.4 P1：Live Draw Engine 测试。

覆盖：事件总线 / 开奖日程 / check_once 各分支 / should_check / sync_all / 后台循环。
"""
from __future__ import annotations

import threading
from datetime import date, datetime, timedelta

import pytest

from engine.live_draw import (
    DrawEvent, DrawEventBus, LiveDrawService, on_draw_updated, on_new_issue, sync_now,
)
from engine.ticket_system.schedule import LotterySchedule


class FakeUpdater:
    """模拟 IncrementalUpdater。"""

    def __init__(self, lottery="dlt", storage_dir=None, result=None, local=None):
        self.lottery = lottery
        self._result = result or {"updated": False, "reason": "no_new",
                                  "added": 0, "total": 0}
        self._local = local or []

    def update(self, force=False, pages=1):
        return dict(self._result)

    def load_local(self):
        return list(self._local)

    def _load_builtin(self):
        return list(self._local)

    def _last_update(self):
        return None


@pytest.fixture()
def service(tmp_path):
    return LiveDrawService(storage_dir=str(tmp_path))


@pytest.fixture()
def bus():
    DrawEventBus.reset()
    yield DrawEventBus
    DrawEventBus.reset()


# ---------- 事件总线 ----------
def test_subscribe_publish(bus):
    got = []
    bus.subscribe("draw_updated", lambda e: got.append(e.issue))
    bus.publish(DrawEvent(event_type="draw_updated", lottery="dlt", issue="26087"))
    assert got == ["26087"]


def test_publish_unknown_type(bus):
    got = []
    bus.subscribe("draw_updated", lambda e: got.append(1))
    bus.publish(DrawEvent(event_type="hacker", lottery="dlt"))
    assert got == []  # 未知类型无人订阅


def test_on_draw_updated_decorator(bus):
    got = []

    @on_draw_updated
    def cb(e):
        got.append(e.lottery)

    bus.publish(DrawEvent(event_type="draw_updated", lottery="dlt"))
    assert got == ["dlt"]


def test_on_new_issue_decorator(bus):
    got = []

    @on_new_issue
    def cb(e):
        got.append(e.issue)

    bus.publish(DrawEvent(event_type="new_issue", lottery="dlt", issue="26088"))
    assert got == ["26088"]


def test_bus_reset(bus):
    bus.subscribe("draw_updated", lambda e: None)
    bus.reset()
    assert bus.subscriber_count("draw_updated") == 0


def test_event_to_dict():
    ev = DrawEvent(event_type="draw_updated", lottery="dlt", issue="26087",
                   draw_date="2026-08-03", added=1, total=1201)
    d = ev.to_dict()
    assert d["issue"] == "26087"
    assert d["lottery_name"] == "大乐透"


def test_event_lottery_name_ssq():
    ev = DrawEvent(event_type="draw_updated", lottery="ssq")
    assert ev.lottery_name == "双色球"


# ---------- 开奖日程 ----------
@pytest.mark.parametrize("lottery,weekday,expect", [
    ("dlt", 0, True), ("dlt", 2, True), ("dlt", 5, True),
    ("dlt", 1, False), ("dlt", 3, False), ("dlt", 4, False), ("dlt", 6, False),
])
def test_dlt_draw_days(lottery, weekday, expect):
    d = (date(2026, 8, 3) + timedelta(days=weekday)).isoformat()
    assert LotterySchedule.is_draw_day(lottery, d) is expect


@pytest.mark.parametrize("lottery,weekday,expect", [
    ("ssq", 1, True), ("ssq", 3, True), ("ssq", 6, True),
    ("ssq", 0, False), ("ssq", 2, False), ("ssq", 4, False), ("ssq", 5, False),
])
def test_ssq_draw_days(lottery, weekday, expect):
    d = (date(2026, 8, 3) + timedelta(days=weekday)).isoformat()
    assert LotterySchedule.is_draw_day(lottery, d) is expect


def test_next_draw_date_dlt():
    nxt = LotterySchedule.next_draw_date("dlt", "2026-08-03")  # 周一
    assert nxt == "2026-08-03"  # 当天就是开奖日


def test_next_draw_date_ssq():
    nxt = LotterySchedule.next_draw_date("ssq", "2026-08-03")  # 周一
    assert nxt == "2026-08-04"  # 周二


def test_next_draw_date_bad():
    assert LotterySchedule.next_draw_date("dlt", "bad-date") is None


# ---------- check_once：更新成功 ----------
def test_check_once_updated(service, monkeypatch):
    events = []
    service.event_bus.subscribe("draw_updated", lambda e: events.append(e))
    service.event_bus.subscribe("new_issue", lambda e: events.append(e))
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir,
            result={"updated": True, "added": 1, "total": 1201,
                    "error": None, "issue": "26087"}),
    )
    ev = service.check_once("dlt", force=True)
    assert ev.event_type == "draw_updated"
    assert ev.issue in ("26087", "")
    assert len(events) >= 1


# ---------- check_once：无新期 ----------
def test_check_once_no_new(service, monkeypatch):
    events = []
    service.event_bus.subscribe("sync_skipped", lambda e: events.append(e))
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "no_new",
                                          "added": 0, "total": 1201}),
    )
    ev = service.check_once("dlt")
    assert ev.event_type == "sync_skipped"
    assert len(events) == 1


# ---------- check_once：失败 ----------
def test_check_once_failed(service, monkeypatch):
    events = []
    service.event_bus.subscribe("update_failed", lambda e: events.append(e))
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "exception",
                                          "error": "net down"}),
    )
    ev = service.check_once("dlt")
    assert ev.event_type == "update_failed"
    assert ev.error == "net down"
    assert len(events) == 1


def test_check_once_api_empty(service, monkeypatch):
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "no_remote_data"}),
    )
    ev = service.check_once("dlt")
    assert ev.event_type == "update_failed"
    assert ev.reason == "no_remote_data"


# ---------- should_check ----------
def test_should_check_draw_day(service, monkeypatch):
    now = datetime(2026, 8, 4, 10, 0)  # 周二
    # ssq 开奖日 → True
    assert service.should_check("ssq", now) is True


def test_should_check_non_draw_day_no_meta(service, monkeypatch):
    now = datetime(2026, 8, 5, 10, 0)  # 周三（dlt 开奖日）
    # 有 meta 且较新 → 非开奖日判断
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": True}),
    )
    # storage 无 meta → should_check True
    assert service.should_check("dlt", now) is True


# ---------- sync_all ----------
def test_sync_all(service, monkeypatch):
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "no_new",
                                          "added": 0, "total": 1201}),
    )
    events = service.sync_all()
    assert len(events) == 2  # dlt + ssq


# ---------- 后台循环 ----------
def test_auto_sync_loop_stops(service, monkeypatch):
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "no_new",
                                          "added": 0, "total": 1201}),
    )
    stop = threading.Event()
    t = threading.Thread(target=service.auto_sync_loop,
                         kwargs={"interval_seconds": 0.1, "stop_event": stop},
                         daemon=True)
    t.start()
    import time
    time.sleep(0.3)
    stop.set()
    t.join(timeout=2)
    assert not t.is_alive()


# ---------- 便捷函数 ----------
def test_sync_now_returns_list(monkeypatch):
    monkeypatch.setattr(
        "engine.data_center_v2.updater.IncrementalUpdater",
        lambda lottery="dlt", storage_dir=None: FakeUpdater(
            lottery, storage_dir, result={"updated": False, "reason": "no_new",
                                          "added": 0, "total": 1201}),
    )
    evs = sync_now()
    assert isinstance(evs, list)
