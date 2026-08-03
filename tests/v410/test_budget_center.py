"""v4.1 阶段3：预算中心（周/月/年 + 亏损率 + 预警）测试。"""
from __future__ import annotations

import random

import pytest

from engine.budget_manager import BudgetPlanner, BudgetHealthReport


# ---------- 周预算 ----------
def test_week_budget_default():
    bp = BudgetPlanner(storage_dir="/tmp/budget_center_test")
    assert bp.week_budget == 120


def test_set_week_budget(ticket_storage):
    bp = BudgetPlanner()
    bp.set_budget(week_budget=200)
    assert bp.week_budget == 200


def test_set_all_budgets(ticket_storage):
    bp = BudgetPlanner()
    bp.set_budget(week_budget=100, month_budget=400, year_budget=4800)
    assert bp.week_budget == 100
    assert bp.month_budget == 400
    assert bp.year_budget == 4800


def test_week_ratio():
    r = BudgetPlanner.evaluate(60, 300, 3600, 120, 500, 6000)
    assert r.week_ratio == pytest.approx(0.5)


def test_week_over():
    r = BudgetPlanner.evaluate(150, 300, 3600, 120, 500, 6000)
    assert r.week_over is True


def test_week_not_over():
    r = BudgetPlanner.evaluate(100, 300, 3600, 120, 500, 6000)
    assert not r.week_over


# ---------- 亏损率 ----------
def test_loss_rate():
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000, loss_rate=-0.8)
    assert r.loss_rate == -0.8


def test_loss_rate_zero():
    r = BudgetPlanner.evaluate(0, 0, 0)
    assert r.loss_rate == 0


@pytest.mark.parametrize("lr", [-0.9, -0.5, -0.1, 0.1])
def test_loss_rate_matrix(lr):
    r = BudgetPlanner.evaluate(0, 0, 0, loss_rate=lr)
    assert r.loss_rate == lr


def test_loss_rate_suggestion():
    r = BudgetPlanner.evaluate(0, 0, 0, loss_rate=-0.8)
    assert any("亏损率" in s for s in r.suggestions)


# ---------- 预警级别 ----------
def test_warning_normal():
    r = BudgetPlanner.evaluate(50, 200, 2000, 120, 500, 6000)
    assert r.warning_level == "正常"


def test_warning_alert():
    r = BudgetPlanner.evaluate(100, 450, 5000, 120, 500, 6000)
    assert r.warning_level == "预警"


def test_warning_over():
    r = BudgetPlanner.evaluate(150, 600, 6500, 120, 500, 6000)
    assert r.warning_level == "超支"


@pytest.mark.parametrize("week,month,year,level", [
    (50, 200, 2000, "正常"),
    (100, 450, 5000, "预警"),
    (150, 600, 6500, "超支"),
    (90, 400, 4000, "正常"),
])
def test_warning_levels(week, month, year, level):
    r = BudgetPlanner.evaluate(week, month, year, 120, 500, 6000)
    assert r.warning_level == level


# ---------- 报告结构 ----------
def test_report_type():
    r = BudgetPlanner.evaluate(0, 0, 0)
    assert isinstance(r, BudgetHealthReport)


@pytest.mark.parametrize("f", ["week_budget", "week_spent", "week_ratio", "week_over",
                               "loss_rate", "warning_level"])
def test_report_fields(f):
    r = BudgetPlanner.evaluate(0, 0, 0)
    assert hasattr(r, f)


@pytest.mark.parametrize("f", ["week_budget", "week_spent", "week_ratio",
                               "loss_rate", "warning_level"])
def test_report_dict_keys(f):
    r = BudgetPlanner.evaluate(0, 0, 0)
    assert f in r.to_dict()


def test_summary_fields():
    r = BudgetPlanner.evaluate(0, 0, 0)
    t = r.summary_text()
    for kw in ("本周", "本月", "今年", "亏损率", "预警级别"):
        assert kw in t


# ---------- spent_from_tickets 周维度 ----------
def test_week_spent_today():
    from datetime import date
    today = date.today()
    tickets = [{"buy_date": today.isoformat(), "cost": 10.0,
                "front": [1, 2, 3, 4, 5], "back": [6, 7]}]
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert w == pytest.approx(10.0)
    assert m == pytest.approx(10.0)
    assert y == pytest.approx(10.0)


def test_week_spent_ignores_last_week():
    from datetime import date, timedelta
    last = (date.today() - timedelta(days=7)).isoformat()
    tickets = [{"buy_date": last, "cost": 10.0,
                "front": [1, 2, 3, 4, 5], "back": [6, 7]}]
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert w == 0.0


@pytest.mark.parametrize("i", range(10))
def test_week_spent_matrix(i):
    import random
    rng = random.Random(i)
    tickets = []
    for _ in range(5):
        offset = rng.randint(-2, 3)
        from datetime import date, timedelta
        d = (date.today() + timedelta(days=offset)).isoformat()
        tickets.append({"buy_date": d, "cost": 4.0, "front": [1, 2, 3, 4, 5], "back": [6, 7]})
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert w >= 0
    assert w <= y


# ---------- evaluate_tickets 含亏损率 ----------
def test_evaluate_tickets_loss_rate(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    bp = BudgetPlanner()
    r = bp.evaluate_tickets([t.__dict__ for t in mgr.list_all()])
    assert hasattr(r, "loss_rate")
    assert r.loss_rate == -1.0  # 未中奖
    mgr.clear()


def test_evaluate_tickets_week(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    bp = BudgetPlanner()
    r = bp.evaluate_tickets([t.__dict__ for t in mgr.list_all()])
    assert r.week_budget == 120
    mgr.clear()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_budget_center_matrix(seed):
    rng = random.Random(seed)
    week = rng.randint(0, 200)
    month = rng.randint(0, 800)
    year = rng.randint(0, 10000)
    r = BudgetPlanner.evaluate(week, month, year, 120, 500, 6000)
    assert r.warning_level in ("正常", "预警", "超支")
    assert 0 <= r.health_score <= 100
    assert r.week_ratio == pytest.approx(week / 120)
    assert r.month_ratio == pytest.approx(month / 500)


@pytest.mark.parametrize("seed", range(30))
def test_budget_settings_matrix(seed, ticket_storage):
    rng = random.Random(1000 + seed)
    wb = rng.randint(50, 300)
    bp = BudgetPlanner()
    bp.set_budget(week_budget=wb)
    assert BudgetPlanner().week_budget == wb
