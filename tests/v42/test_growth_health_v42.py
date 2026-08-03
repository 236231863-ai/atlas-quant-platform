"""v4.2 Phase 3：购彩健康指数测试。"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.growth_health import (
    DIMENSIONS,
    GrowthHealthEngine,
    GrowthHealthReport,
    HealthDimension,
    growth_health,
)
from engine.budget_manager import BudgetHealthReport


def _budget(health=100, loss=0.0, month_over=False, week_over=False):
    return BudgetHealthReport(
        week_budget=120, month_budget=500, year_budget=6000,
        week_spent=50, month_spent=200, year_spent=2000,
        week_ratio=50 / 120, month_ratio=200 / 500, year_ratio=2000 / 6000,
        week_over=week_over, month_over=month_over, year_over=False,
        exceed_amount=0, loss_rate=loss,
        warning_level="超支" if (month_over or week_over) else "正常",
        health_score=health, suggestions=[],
    )


def _tk(days_ago=3, claimed=False, draw="", cost=2.0, win=False):
    buy = (date.today() - timedelta(days=days_ago)).isoformat()
    if win:
        front, back = [10, 11, 18, 22, 35], [6, 12]
        draw = draw or "2026-08-01"
    else:
        front, back = [1, 2, 3, 4, 5], [6, 7]
    return {"lottery": "dlt", "front": front, "back": back,
            "buy_date": buy, "draw_date": draw, "cost": cost, "claimed": claimed}


# ---------- 空数据 ----------
def test_empty_level_c():
    r = GrowthHealthEngine.evaluate([])
    assert r.rational_level == "C"
    assert r.overall_score == 0


def test_empty_suggestions():
    r = GrowthHealthEngine.evaluate([])
    assert any("保存第一张彩票" in s for s in r.suggestions)


def test_empty_dimensions():
    r = GrowthHealthEngine.evaluate([])
    assert len(r.dimensions) == 4


# ---------- 预算控制 ----------
def test_budget_good_score():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(health=95))
    d = {x.name: x.score for x in r.dimensions}
    assert d["预算控制"] == 95


def test_budget_bad_score():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(health=30))
    d = {x.name: x.score for x in r.dimensions}
    assert d["预算控制"] == 30


def test_budget_none_default():
    r = GrowthHealthEngine.evaluate([_tk()], None)
    d = {x.name: x.score for x in r.dimensions}
    assert d["预算控制"] >= 0


# ---------- 连续记录 ----------
def test_record_empty():
    d = next(x for x in GrowthHealthEngine.evaluate([]).dimensions if x.name == "连续记录")
    assert d.score == 0


def test_record_one_week():
    r = GrowthHealthEngine.evaluate([_tk(days_ago=0)], _budget())
    d = next(x for x in r.dimensions if x.name == "连续记录")
    assert d.score in (45, 30)  # 无连续周 → 30 或开始记录 45


def test_record_four_weeks():
    tickets = [_tk(days_ago=7 * w) for w in range(4)]
    r = GrowthHealthEngine.evaluate(tickets, _budget())
    d = next(x for x in r.dimensions if x.name == "连续记录")
    assert d.score >= 70


def test_record_streak_high():
    tickets = [_tk(days_ago=7 * w) for w in range(5)]
    r = GrowthHealthEngine.evaluate(tickets, _budget())
    d = next(x for x in r.dimensions if x.name == "连续记录")
    assert d.score == 100


# ---------- 复盘习惯 ----------
def test_review_no_settled():
    r = GrowthHealthEngine.evaluate([_tk(draw="")], _budget())
    d = next(x for x in r.dimensions if x.name == "复盘习惯")
    assert d.score == 50


def test_review_all_claimed():
    tickets = [_tk(draw="2026-08-01", claimed=True), _tk(draw="2026-08-01", claimed=True)]
    r = GrowthHealthEngine.evaluate(tickets, _budget())
    d = next(x for x in r.dimensions if x.name == "复盘习惯")
    assert d.score >= 70


def test_review_none_claimed():
    tickets = [_tk(draw="2026-08-01", claimed=False)]
    r = GrowthHealthEngine.evaluate(tickets, _budget())
    d = next(x for x in r.dimensions if x.name == "复盘习惯")
    assert d.score == 10


def test_review_partial():
    tickets = [_tk(draw="2026-08-01", claimed=True), _tk(draw="2026-08-01", claimed=False)]
    r = GrowthHealthEngine.evaluate(tickets, _budget())
    d = next(x for x in r.dimensions if x.name == "复盘习惯")
    assert 40 <= d.score < 80


# ---------- 风险意识 ----------
def test_risk_good():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(loss=0.0))
    d = next(x for x in r.dimensions if x.name == "风险意识")
    assert d.score >= 90


def test_risk_heavy_loss():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(loss=-0.8))
    d = next(x for x in r.dimensions if x.name == "风险意识")
    assert d.score < 60


def test_risk_month_over():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(month_over=True, loss=-0.1))
    d = next(x for x in r.dimensions if x.name == "风险意识")
    assert d.score <= 75


# ---------- 理性等级 ----------
def test_level_a():
    r = GrowthHealthEngine.evaluate([_tk(claimed=True, draw="2026-08-01")],
                                    _budget(health=100, loss=0.0))
    assert r.rational_level == "A"
    assert r.overall_score >= 80


def test_level_b():
    # 中等：预算健康 60 + 已确认复盘 → 总分 60~80 区间 → B
    r = GrowthHealthEngine.evaluate([_tk(days_ago=0, claimed=True, draw="2026-08-01")],
                                    _budget(health=60, loss=-0.4))
    assert r.rational_level == "B"
    assert 60 <= r.overall_score < 80


def test_level_c():
    r = GrowthHealthEngine.evaluate([_tk()], _budget(health=20, loss=-0.8, month_over=True))
    assert r.rational_level == "C"
    assert r.overall_score < 60


def test_level_text():
    assert GrowthHealthReport(rational_level="A").level_text == "理性 A 级"


# ---------- 红线：不是中奖能力 ----------
def test_not_winning_capability():
    """中奖再多，超预算+高亏损 → 低等级。"""
    tickets = [_tk(win=True, claimed=True, days_ago=0)]  # 中一等奖
    r = GrowthHealthEngine.evaluate(tickets, _budget(health=15, loss=-0.9, month_over=True))
    assert r.rational_level != "A"
    assert r.overall_score < 60


def test_winning_does_not_boost_level():
    """同样的健康行为，中不中奖不影响等级。"""
    win_tk = [_tk(win=True, claimed=True, draw="2026-08-01")]
    miss_tk = [_tk(claimed=True, draw="2026-08-01")]
    b = _budget(health=100, loss=0.0)
    rw = GrowthHealthEngine.evaluate(win_tk, b)
    rm = GrowthHealthEngine.evaluate(miss_tk, b)
    assert rw.rational_level == rm.rational_level
    assert abs(rw.overall_score - rm.overall_score) <= 2


def test_disclaimer_not_gambling():
    r = GrowthHealthEngine.evaluate([])
    assert "不代表中奖能力" in r.disclaimer
    for bad in ("稳赚", "必中", "保证", "预测中奖"):
        assert bad not in r.summary_text()


# ---------- 输出 ----------
def test_to_dict():
    r = GrowthHealthEngine.evaluate([_tk()], _budget())
    d = r.to_dict()
    assert d["overall_score"] >= 0
    assert d["rational_level"] in ("A", "B", "C")
    assert len(d["dimensions"]) == 4
    assert "disclaimer" in d


def test_summary_text():
    r = GrowthHealthEngine.evaluate([_tk()], _budget())
    s = r.summary_text()
    assert "健康指数" in s
    assert "理性" in s
    assert "预算控制" in s


def test_dimension_weight_sum():
    r = GrowthHealthEngine.evaluate([_tk()], _budget())
    total = sum(x.weight for x in r.dimensions)
    assert abs(total - 1.0) < 1e-6


def test_dimension_order():
    r = GrowthHealthEngine.evaluate([_tk()], _budget())
    names = [x.name for x in r.dimensions]
    assert names == list(DIMENSIONS)


# ---------- 便捷函数 ----------
def test_growth_health_func():
    r = growth_health([_tk()], _budget())
    assert isinstance(r, GrowthHealthReport)


# ---------- 参数化矩阵 ----------
@pytest.mark.parametrize("health", [0, 30, 60, 85, 100])
def test_budget_dimension_matrix(health):
    r = GrowthHealthEngine.evaluate([_tk()], _budget(health=health))
    d = next(x for x in r.dimensions if x.name == "预算控制")
    assert d.score == health


@pytest.mark.parametrize("loss", [-0.9, -0.6, -0.4, -0.2, -0.05, 0.0, 0.3])
def test_risk_loss_matrix(loss):
    r = GrowthHealthEngine.evaluate([_tk()], _budget(loss=loss))
    d = next(x for x in r.dimensions if x.name == "风险意识")
    assert 0 <= d.score <= 100
    # 亏损越重，风险分越低（单调非增）
    if loss < -0.5:
        assert d.score < 65
    elif loss > -0.1:
        assert d.score >= 80


@pytest.mark.parametrize("seed", range(25))
def test_growth_random_matrix(seed):
    rng = random.Random(seed)
    n = rng.randint(0, 8)
    tickets = [_tk(days_ago=rng.randint(0, 40),
                   claimed=rng.random() < 0.5,
                   draw="2026-08-01" if rng.random() < 0.5 else "",
                   cost=rng.randint(2, 30)) for _ in range(n)]
    r = GrowthHealthEngine.evaluate(tickets, _budget(health=rng.randint(20, 100),
                                                     loss=rng.uniform(-0.8, 0.2)))
    assert 0 <= r.overall_score <= 100
    assert r.rational_level in ("A", "B", "C")
    assert len(r.dimensions) == 4
    assert r.ticket_count == n
    s = r.summary_text()
    assert isinstance(s, str) and len(s) > 10


@pytest.mark.parametrize("seed", range(15))
def test_growth_auto_budget(seed, ticket_storage):
    """自动计算预算路径（默认预算 + 少量票 → 预算内高分）。"""
    from engine.ticket_system import TicketManager
    rng = random.Random(seed)
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 3)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01", cost=2.0)
    tickets = [t.__dict__ for t in mgr.list_all()]
    r = GrowthHealthEngine.evaluate(tickets)
    assert r.rational_level in ("A", "B", "C")
    assert r.ticket_count >= 1
    mgr.clear()


@pytest.mark.parametrize("seed", range(15))
def test_growth_full_flow(seed, ticket_storage):
    """全流程：保存→复盘确认→健康评估。"""
    from engine.ticket_system import TicketManager
    rng = random.Random(1000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 4)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01",
                draw_date="2026-08-01", cost=2.0)
    tickets = [t.__dict__ for t in mgr.list_all()]
    for t in tickets:
        t["claimed"] = True
    r = GrowthHealthEngine.evaluate(tickets)
    assert r.overall_score >= 0
    assert "复盘习惯" in r.summary_text()
    mgr.clear()
