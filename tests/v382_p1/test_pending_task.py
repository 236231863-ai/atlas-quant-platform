"""v3.8.2-P1 Phase 1：PendingTaskManager（确认词 / CRUD / 持久化 / 过期）。"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import pytest

from engine.task_context import PendingTaskManager
from engine.task_context.manager import PendingTask

SAMPLE_TICKETS = [
    {"front": [10, 11, 18, 22, 35], "back": [6, 12]},
    {"front": [1, 2, 3, 4, 5], "back": [6, 7]},
]


def _mk(mgr, user="default", tickets=None, **kw):
    return mgr.create_task(user, task_type="prize", lottery_type="dlt",
                           tickets=tickets or SAMPLE_TICKETS,
                           purchase_date="2026-07-31", draw_date="2026-08-01", **kw)


# ---------- 确认词 ----------
CONFIRM_CASES = [
    ("是", True), ("是的", True), ("嗯", True), ("好的", True), ("好", True),
    ("确认", True), ("确定", True), ("确认了", True), ("对", True), ("对的", True),
    ("可以", True), ("行", True), ("没问题", True), ("没错", True),
    ("按这个算", True), ("按这个开奖算", True), ("按8月1日算", True),
    ("按2026-08-01开奖计算", True), ("按这个来算", True),
    ("是的，按这个算", True), ("好的按这个算", True),
    ("嗯好，就这么算", True), ("行吧按这个", True),
]
DENY_CASES = [
    ("不是", False), ("不", False), ("不对", False), ("不要", False),
    ("别算了", False), ("不行", False), ("没有", False), ("无需", False),
    ("为什么要算", False), ("等等", False), ("先别", False),
    ("我买的是大乐透", False), ("这期没中吧", False), ("普通问题", False),
    ("帮我推荐号码", False), ("今天天气如何", False), ("热号有哪些", False),
]


@pytest.mark.parametrize("text,expected", CONFIRM_CASES)
def test_confirm_words(text, expected):
    assert PendingTaskManager.is_confirm_reply(text) == expected


@pytest.mark.parametrize("text,expected", DENY_CASES)
def test_deny_words(text, expected):
    assert PendingTaskManager.is_confirm_reply(text) == expected


# ---------- create / get ----------
def test_create_task(task_storage):
    mgr = PendingTaskManager()
    t = _mk(mgr)
    assert t.user_id == "default"
    assert t.task_type == "prize"
    assert t.lottery_type == "dlt"
    assert t.note_count == 2
    assert t.purchase_date == "2026-07-31"
    assert t.draw_date == "2026-08-01"
    assert t.created_time
    assert t.expire_time


def test_get_pending_task(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr)
    t = mgr.get_pending_task("default")
    assert t is not None
    assert t.note_count == 2
    assert t.tickets[0]["front"] == [10, 11, 18, 22, 35]


def test_get_none_when_empty(task_storage):
    mgr = PendingTaskManager()
    assert mgr.get_pending_task("default") is None
    assert not mgr.has_pending("default")


def test_confirm_task_returns_and_clears(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr)
    t = mgr.confirm_task("default")
    assert t is not None
    assert t.note_count == 2
    assert not mgr.has_pending("default")


def test_confirm_task_empty(task_storage):
    mgr = PendingTaskManager()
    assert mgr.confirm_task("default") is None


def test_clear_task(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr)
    assert mgr.clear_task("default") is True
    assert not mgr.has_pending("default")


def test_clear_task_empty(task_storage):
    mgr = PendingTaskManager()
    assert mgr.clear_task("default") is False


def test_create_overwrites_old(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr, tickets=[{"front": [1, 2, 3, 4, 5], "back": [6, 7]}])
    _mk(mgr, tickets=SAMPLE_TICKETS)
    t = mgr.get_pending_task("default")
    assert t.note_count == 2


# ---------- 多用户隔离 ----------
@pytest.mark.parametrize("user", ["u1", "u2", "u3", "alice", "bob", "test_user_01"])
def test_multi_user_isolated(task_storage, user):
    mgr = PendingTaskManager()
    _mk(mgr, user=user)
    assert mgr.has_pending(user)
    assert not mgr.has_pending("someone_else")


# ---------- 持久化（重启恢复）----------
def test_restart_persists(task_storage):
    _mk(PendingTaskManager())
    # 模拟重启：新实例读同一目录
    mgr2 = PendingTaskManager()
    t = mgr2.get_pending_task("default")
    assert t is not None
    assert t.purchase_date == "2026-07-31"


def test_restart_after_confirm_gone(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr)
    mgr.confirm_task("default")
    mgr2 = PendingTaskManager()
    assert mgr2.get_pending_task("default") is None


def test_storage_file_created(task_storage):
    _mk(PendingTaskManager())
    path = os.path.join(task_storage, "pending_tasks_v382.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert "default" in data


# ---------- 过期 ----------
@pytest.mark.parametrize("minutes,expired", [
    (1, False), (30, False), (60, False), (-1, True), (-60, True),
])
def test_expiry(task_storage, minutes, expired):
    mgr = PendingTaskManager()
    _mk(mgr, expire_minutes=minutes)
    if expired:
        assert mgr.get_pending_task("default") is None
    else:
        assert mgr.get_pending_task("default") is not None


def test_expired_auto_cleared(task_storage):
    mgr = PendingTaskManager()
    t = _mk(mgr, expire_minutes=-1)
    assert mgr.get_pending_task("default") is None
    # 已自动清除
    assert "default" not in mgr._tasks


def test_future_expire_time(task_storage):
    mgr = PendingTaskManager()
    t = _mk(mgr)
    exp = datetime.strptime(t.expire_time, "%Y-%m-%d %H:%M:%S")
    assert exp > datetime.now()


# ---------- 字段完整性 ----------
@pytest.mark.parametrize("field", [
    "user_id", "task_type", "lottery_type", "tickets", "purchase_date",
    "draw_date", "issue", "created_time", "expire_time",
])
def test_required_fields(task_storage, field):
    t = _mk(PendingTaskManager())
    assert hasattr(t, field)
    assert field in t.to_dict()


def test_issue_field(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr, issue="26086")
    t = mgr.get_pending_task("default")
    assert t.issue == "26086"


def test_ticket_front_back_accessor(task_storage):
    mgr = PendingTaskManager()
    _mk(mgr)
    t = mgr.get_pending_task("default")
    f, b = t.ticket_front_back(0)
    assert f == [10, 11, 18, 22, 35]
    assert b == [6, 12]


def test_note_count_field(task_storage):
    _mk(PendingTaskManager())
    t = PendingTaskManager().get_pending_task("default")
    assert t.note_count == 2
