"""v4.0.0 Phase 2：个人资金管理测试。"""
from __future__ import annotations

import json
import os

import pytest

from engine.budget_manager import BudgetPlanner, BudgetHealthReport, BudgetSettings
from engine.budget_manager.budget import DEFAULT_MONTH_BUDGET, DEFAULT_YEAR_BUDGET


# ---------- 默认设置 ----------
def test_default_settings():
    bp = BudgetPlanner(storage_dir="/tmp/budget_default_test")
    assert bp.month_budget == DEFAULT_MONTH_BUDGET
    assert bp.year_budget == DEFAULT_YEAR_BUDGET


def test_settings_type():
    s = BudgetSettings()
    assert isinstance(s.month_budget, float)


# ---------- 设置预算 ----------
def test_set_month_budget(task_storage):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=300)
    assert bp.month_budget == 300


def test_set_year_budget(task_storage):
    bp = BudgetPlanner()
    bp.set_budget(year_budget=4000)
    assert bp.year_budget == 4000


def test_set_both(task_storage):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=200, year_budget=2400)
    assert bp.month_budget == 200
    assert bp.year_budget == 2400


def test_set_returns_settings(task_storage):
    bp = BudgetPlanner()
    s = bp.set_budget(month_budget=150)
    assert isinstance(s, BudgetSettings)
    assert s.month_budget == 150


@pytest.mark.parametrize("mb,yb", [(100, 1200), (500, 6000), (1000, 12000), (0, 0)])
def test_set_budget_matrix(task_storage, mb, yb):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=mb, year_budget=yb)
    assert bp.month_budget == mb
    assert bp.year_budget == yb


# ---------- 持久化 ----------
def test_persist(task_storage):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=300, year_budget=3600)
    bp2 = BudgetPlanner()
    assert bp2.month_budget == 300
    assert bp2.year_budget == 3600


def test_file_created(task_storage):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=250)
    path = os.path.join(task_storage, "budget_v400.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    assert d["month_budget"] == 250


# ---------- evaluate 公式 ----------
def test_evaluate_ratio():
    r = BudgetPlanner.evaluate(week_spent=0, month_spent=250, year_spent=3000, week_budget=120,
                               month_budget=500, year_budget=6000)
    assert r.month_ratio == pytest.approx(0.5)
    assert r.year_ratio == pytest.approx(0.5)


def test_evaluate_over_month():
    r = BudgetPlanner.evaluate(0, 600, 3000, 120, 500, 6000)
    assert r.month_over is True
    assert r.month_ratio == pytest.approx(1.2)


def test_evaluate_over_year():
    r = BudgetPlanner.evaluate(0, 200, 6500, 120, 500, 6000)
    assert r.year_over is True


def test_evaluate_not_over():
    r = BudgetPlanner.evaluate(0, 100, 1000, 120, 500, 6000)
    assert not r.month_over
    assert not r.year_over


def test_evaluate_exceed_amount():
    r = BudgetPlanner.evaluate(0, 600, 3000, 120, 500, 6000)
    assert r.exceed_amount == pytest.approx(100)


def test_evaluate_no_exceed():
    r = BudgetPlanner.evaluate(0, 200, 1000, 120, 500, 6000)
    assert r.exceed_amount == 0


@pytest.mark.parametrize("month,year", [
    (100, 1200), (250, 3000), (500, 6000), (750, 9000), (0, 0),
])
def test_evaluate_ratio_consistency(month, year):
    r = BudgetPlanner.evaluate(0, month, year, 120, 500, 6000)
    assert r.month_ratio == pytest.approx(month / 500)
    assert r.year_ratio == pytest.approx(year / 6000)


# ---------- 健康度 ----------
def test_health_full():
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert r.health_score == 100


def test_health_deducted():
    r = BudgetPlanner.evaluate(0, 450, 3600, 120, 500, 6000)
    assert r.health_score < 100


def test_health_over():
    r = BudgetPlanner.evaluate(0, 1000, 10000, 120, 500, 6000)
    assert r.health_score < 50


@pytest.mark.parametrize("month,year", [
    (0, 0), (200, 2000), (400, 4800), (600, 6500), (1000, 12000),
])
def test_health_range(month, year):
    r = BudgetPlanner.evaluate(0, month, year, 120, 500, 6000)
    assert 0 <= r.health_score <= 100


# ---------- spent_from_tickets ----------
def _tk(buy_date, cost=2.0):
    return {"buy_date": buy_date, "cost": cost, "front": [1, 2, 3, 4, 5], "back": [6, 7]}


def test_spent_empty():
    w, m, y = BudgetPlanner.spent_from_tickets([])
    assert m == 0 and y == 0


def test_spent_this_year():
    from datetime import date
    today = date.today()
    tickets = [_tk(f"{today.year}-01-15"), _tk(f"{today.year}-07-01")]
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert y == pytest.approx(4.0)


def test_spent_last_year_ignored():
    from datetime import date
    today = date.today()
    tickets = [_tk(f"{today.year - 1}-07-01")]
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert y == 0


@pytest.mark.parametrize("i", range(10))
def test_spent_matrix(i):
    from datetime import date
    today = date.today()
    tickets = []
    for _ in range(5):
        tickets.append(_tk(f"{today.year}-{i % 12 + 1:02d}-15", cost=4.0))
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert y == pytest.approx(20.0)


# ---------- evaluate_tickets ----------
def test_evaluate_tickets(task_storage):
    from datetime import date
    today = date.today()
    bp = BudgetPlanner()
    bp.set_budget(month_budget=100, year_budget=1200)
    tickets = [_tk(f"{today.year}-{today.month:02d}-05", cost=50.0)]
    r = bp.evaluate_tickets(tickets)
    assert r.month_spent == pytest.approx(50.0)
    assert r.month_ratio == pytest.approx(0.5)


# ---------- 报告结构 ----------
def test_report_type():
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert isinstance(r, BudgetHealthReport)


@pytest.mark.parametrize("f", ["month_budget", "year_budget", "month_spent",
                               "year_spent", "month_ratio", "year_ratio",
                               "month_over", "year_over", "health_score"])
def test_report_fields(f):
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert hasattr(r, f)


@pytest.mark.parametrize("f", ["month_budget", "month_ratio", "health_score"])
def test_report_dict_keys(f):
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert f in r.to_dict()


def test_summary_fields():
    r = BudgetPlanner.evaluate(0, 100, 1000, 120, 500, 6000)
    t = r.summary_text()
    for kw in ("本周", "本月", "今年", "亏损率", "预警级别"):
        assert kw in t


# ---------- 建议 ----------
def test_suggestions_over():
    r = BudgetPlanner.evaluate(0, 600, 3000, 120, 500, 6000)
    assert any("超" in s or "暂停" in s for s in r.suggestions)


def test_suggestions_warning():
    r = BudgetPlanner.evaluate(0, 450, 3000, 120, 500, 6000)
    assert any("注意" in s or "控制" in s for s in r.suggestions)


def test_suggestions_ok():
    r = BudgetPlanner.evaluate(0, 100, 1000, 120, 500, 6000)
    assert any("良好" in s or "保持" in s for s in r.suggestions)


# ---------- 免责声明 ----------
def test_disclaimer():
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert "随机性" in r.disclaimer
    assert "预测" not in r.disclaimer


def test_summary_has_disclaimer():
    r = BudgetPlanner.evaluate(0, 0, 0, 120, 500, 6000)
    assert "随机性" in r.summary_text()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_budget_param_matrix(seed):
    import random
    rng = random.Random(seed)
    mb = rng.choice([100, 200, 500, 1000])
    yb = mb * 12
    spent = rng.randint(0, int(mb * 1.5))
    r = BudgetPlanner.evaluate(0, spent, spent * 6, 120, mb, yb)
    assert r.month_budget == mb
    assert r.month_ratio >= 0
    assert 0 <= r.health_score <= 100


@pytest.mark.parametrize("seed", range(30))
def test_over_flag_matrix(seed):
    import random
    rng = random.Random(1000 + seed)
    mb = 500
    spent = rng.randint(int(mb * 0.5), int(mb * 1.5))
    r = BudgetPlanner.evaluate(0, spent, 1000, 120, mb, 6000)
    assert r.month_over == (spent > mb)


@pytest.mark.parametrize("seed", range(30))
def test_settings_persist_matrix(seed, task_storage):
    import random
    rng = random.Random(2000 + seed)
    mb = rng.randint(50, 1000)
    bp = BudgetPlanner()
    bp.set_budget(month_budget=mb)
    assert BudgetPlanner().month_budget == mb


@pytest.mark.parametrize("seed", range(40))
def test_evaluate_health_matrix(seed):
    import random
    rng = random.Random(3000 + seed)
    mb = rng.choice([200, 500, 800])
    yb = mb * 12
    for _ in range(3):
        spent = rng.randint(0, int(mb * 2))
        r = BudgetPlanner.evaluate(0, spent, spent * 6, 120, mb, yb)
        assert 0 <= r.health_score <= 100
        assert r.month_ratio == pytest.approx(spent / mb, abs=0.001)


@pytest.mark.parametrize("seed", range(30))
def test_spent_dates_matrix(seed):
    import random
    from datetime import date
    rng = random.Random(4000 + seed)
    today = date.today()
    tickets = [_tk(f"{today.year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                   cost=2.0 * rng.randint(1, 5)) for _ in range(5)]
    w, m, y = BudgetPlanner.spent_from_tickets(tickets)
    assert y == pytest.approx(sum(t["cost"] for t in tickets))
    assert 0 <= m <= y


@pytest.mark.parametrize("mb", [100, 200, 500, 1000, 2000])
def test_over_detection_boundary(mb):
    r = BudgetPlanner.evaluate(0, mb, mb * 12, 120, mb, mb * 12)
    assert r.month_ratio == pytest.approx(1.0)
    assert not r.month_over  # 正好等于预算不算超额
