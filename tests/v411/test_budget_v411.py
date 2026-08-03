"""v4.1.1 Phase 4：预算管家强化测试（提醒/连续购买）。"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.budget_manager import BudgetPlanner


def _tk(days_ago, cost=2.0):
    return {"buy_date": (date.today() - timedelta(days=days_ago)).isoformat(),
            "cost": cost, "front": [1, 2, 3, 4, 5], "back": [6, 7]}


# ---------- 连续购买周数 ----------
def test_consecutive_weeks_empty():
    assert BudgetPlanner.consecutive_weeks([]) == 0


def test_consecutive_weeks_one():
    assert BudgetPlanner.consecutive_weeks([_tk(0)]) >= 1


def test_consecutive_weeks_four():
    tickets = [_tk(7 * w) for w in range(4)]
    assert BudgetPlanner.consecutive_weeks(tickets) >= 3


def test_consecutive_weeks_broken():
    # 间隔 14 天 → 断裂
    tickets = [_tk(0), _tk(21)]
    assert BudgetPlanner.consecutive_weeks(tickets) <= 2


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_consecutive_weeks_matrix(n):
    tickets = [_tk(7 * w) for w in range(n)]
    assert BudgetPlanner.consecutive_weeks(tickets) >= n - 1


# ---------- 预算提醒 ----------
def test_reminder_week_80():
    tickets = [_tk(0, cost=25.0)]
    bp = BudgetPlanner()
    bp.set_budget(week_budget=30)
    tips = BudgetPlanner.reminders(tickets)
    assert any("预算" in t and "%" in t for t in tips)


def test_reminder_consecutive():
    tickets = [_tk(7 * w, cost=2.0) for w in range(4)]
    tips = BudgetPlanner.reminders(tickets)
    assert any("连续购买" in t for t in tips)


def test_reminder_month_over():
    tickets = [_tk(0, cost=600.0)]
    bp = BudgetPlanner()
    bp.set_budget(month_budget=500, year_budget=6000)
    tips = BudgetPlanner.reminders(tickets)
    assert any("超预算" in t for t in tips)


def test_reminder_no_crash_empty():
    assert BudgetPlanner.reminders([]) == []


@pytest.mark.parametrize("seed", range(30))
def test_reminder_matrix(seed):
    rng = random.Random(seed)
    tickets = [_tk(rng.randint(0, 30), cost=rng.randint(1, 50)) for _ in range(rng.randint(0, 8))]
    tips = BudgetPlanner.reminders(tickets)
    assert isinstance(tips, list)
    for t in tips:
        assert "预测" not in t and "稳赚" not in t  # 禁止赌博诱导


# ---------- 禁止赌博诱导 ----------
def test_no_gambling_induction():
    tickets = [_tk(0, cost=100.0)]
    tips = BudgetPlanner.reminders(tickets)
    for t in tips:
        assert "稳赚" not in t and "必中" not in t and "保证" not in t
