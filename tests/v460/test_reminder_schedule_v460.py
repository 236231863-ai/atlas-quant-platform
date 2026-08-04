"""v4.6 P2：Windows 后台提醒计划测试。

覆盖：24h/3h/开奖后提醒计划 / 去重 / 计划任务唤醒逻辑。
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta

import pytest

from engine.draw_monitor.reminder_schedule import (
    LOTTERY_NAMES, ReminderPlan, ReminderScheduler,
)


# 固定开奖日：2026-08-05（周三，大乐透开奖日，20:00 基准）
DRAW_DAY = datetime(2026, 8, 5)


def _now(hour=10):
    return DRAW_DAY.replace(hour=hour)


# ---------- 计划生成 ----------
def test_plan_pre_24h():
    """距开奖 <=24h 且 >3h → pre_24h。"""
    plans = ReminderScheduler.build_plan("dlt", _now(10))
    kinds = {p.kind for p in plans}
    assert "pre_24h" in kinds


def test_plan_pre_3h():
    now = _now(18)  # 18:00，距 20:00 开奖 2h
    plans = ReminderScheduler.build_plan("dlt", now)
    assert "pre_3h" in {p.kind for p in plans}


def test_plan_after_draw():
    now = _now(21)  # 21:00 已过 20:00 开奖
    plans = ReminderScheduler.build_plan("dlt", now)
    assert "after_draw" in {p.kind for p in plans}


def test_plan_empty_far():
    """非开奖日且距开奖 >24h 无提醒。"""
    now = datetime(2026, 8, 2, 10)  # 周日，大乐透下个开奖周三 >24h
    plans = ReminderScheduler.build_plan("dlt", now)
    assert plans == []


def test_plan_title_contains_lottery():
    plans = ReminderScheduler.build_plan("dlt", _now(10))
    assert any("大乐透" in p.title for p in plans)


# ---------- 去重 ----------
def test_already_sent_false(tmp_path):
    assert ReminderScheduler.already_sent("dlt", "pre_24h", str(tmp_path)) is False


def test_mark_then_already_sent(tmp_path):
    ReminderScheduler._mark_sent("dlt:pre_24h", str(tmp_path))
    assert ReminderScheduler.already_sent("dlt", "pre_24h", str(tmp_path)) is True


def test_due_reminders_dedup(tmp_path):
    due = ReminderScheduler.due_reminders("dlt", _now(10), str(tmp_path))
    assert len(due) >= 1
    ReminderScheduler.mark_reminders_sent(due, str(tmp_path))
    due2 = ReminderScheduler.due_reminders("dlt", _now(11), str(tmp_path))
    # 同类型当天不再发
    sent_kinds = {p.kind for p in due}
    assert not any(p.kind in sent_kinds for p in due2)


def test_mark_sent_creates_file(tmp_path):
    ReminderScheduler._mark_sent("dlt:pre_24h", str(tmp_path))
    p = ReminderScheduler._sent_path(str(tmp_path))
    assert os.path.exists(p)
    with open(p, encoding="utf-8") as f:
        assert json.load(f)["dlt:pre_24h"] == date.today().isoformat()


# ---------- 计划结构 ----------
def test_plan_to_dict():
    p = ReminderPlan("dlt", "pre_24h", "2026-08-04T10:00:00", "标题", "消息")
    d = p.to_dict()
    assert d["kind"] == "pre_24h"
    assert d["title"] == "标题"


def test_lottery_names():
    assert LOTTERY_NAMES["dlt"] == "大乐透"
    assert LOTTERY_NAMES["ssq"] == "双色球"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("hour,expect", [
    (10, "pre_24h"), (18, "pre_3h"), (21, "after_draw"),
])
def test_plan_by_hour(hour, expect):
    plans = ReminderScheduler.build_plan("dlt", _now(hour))
    assert expect in {p.kind for p in plans}


@pytest.mark.parametrize("lottery,base", [
    ("dlt", datetime(2026, 8, 5, 10)),   # 周三（大乐透开奖日）
    ("ssq", datetime(2026, 8, 6, 10)),   # 周四（双色球开奖日）
])
def test_plan_lotteries(lottery, base):
    plans = ReminderScheduler.build_plan(lottery, base)
    assert len(plans) >= 1


@pytest.mark.parametrize("i", range(10))
def test_reminder_dedup_stable(tmp_path, i):
    ReminderScheduler._mark_sent(f"dlt:pre_24h", str(tmp_path))
    assert ReminderScheduler.already_sent("dlt", "pre_24h", str(tmp_path)) is True
