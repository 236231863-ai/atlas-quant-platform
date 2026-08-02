"""v3.9.0 Phase 4：资金风险引擎测试。"""
from __future__ import annotations

import pytest

from engine.lottery_quant.risk import RiskEngine, RiskReport, analyze_risk
from engine.lottery_quant.risk.engine import _risk_level

N = 50  # 模拟年数（测试用，保证快）


# ---------- 公式一致性 ----------
@pytest.mark.parametrize("cost,notes,draws,weeks", [
    (2, 1, 3, 52), (2, 15, 3, 52), (10, 5, 2, 52),
    (2, 1, 1, 52), (2, 1, 3, 26), (5, 2, 4, 12),
    (2, 30, 1, 52), (3, 1, 7, 52), (2, 1, 1, 1),
])
def test_annual_investment_formula(cost, notes, draws, weeks):
    r = analyze_risk(cost_per_note=cost, notes_per_draw=notes,
                     draws_per_week=draws, weeks=weeks, n_years=N)
    assert r.annual_investment == cost * notes * draws * weeks


@pytest.mark.parametrize("cost,notes,draws,weeks", [
    (2, 1, 3, 52), (2, 15, 3, 52), (2, 1, 1, 52),
])
def test_annual_draws(cost, notes, draws, weeks):
    r = analyze_risk(cost_per_note=cost, notes_per_draw=notes,
                     draws_per_week=draws, weeks=weeks, n_years=N)
    assert r.annual_draws == draws * weeks


@pytest.mark.parametrize("cost,notes,draws,weeks", [
    (2, 1, 3, 52), (2, 15, 3, 52), (10, 5, 2, 52),
])
def test_max_loss_equals_investment(cost, notes, draws, weeks):
    r = analyze_risk(cost_per_note=cost, notes_per_draw=notes,
                     draws_per_week=draws, weeks=weeks, n_years=N)
    assert r.max_loss == r.annual_investment


def test_expected_return_formula():
    r = analyze_risk(cost_per_note=2, notes_per_draw=15, draws_per_week=3,
                     weeks=52, n_years=N)
    assert r.expected_return == pytest.approx(r.annual_investment * 0.55, rel=0.01)


# ---------- 风险等级边界 ----------
@pytest.mark.parametrize("amount,level", [
    (0, "A"), (500, "A"), (1000, "A"),
    (1000.01, "B"), (2000, "B"), (3000, "B"),
    (3000.01, "C"), (5000, "C"), (10000, "C"),
    (10000.01, "D"), (20000, "D"), (100000, "D"),
])
def test_risk_level_boundaries(amount, level):
    assert _risk_level(amount) == level


@pytest.mark.parametrize("amount,level", [
    (104, "A"), (4680, "C"), (18720, "D"), (312, "A"),
])
def test_risk_level_scenarios(amount, level):
    assert _risk_level(amount) == level


# ---------- 亏损概率 ----------
@pytest.mark.parametrize("i", range(15))
def test_lose_probability_bounded(i):
    r = analyze_risk(cost_per_note=2, notes_per_draw=5, draws_per_week=3,
                     weeks=52, n_years=40, seed=i)
    assert 0.0 <= r.lose_probability <= 1.0


@pytest.mark.parametrize("i", range(10))
def test_lose_probability_high(i):
    """长期彩票投注亏损概率应 > 0.5（负期望游戏）。"""
    r = analyze_risk(cost_per_note=2, notes_per_draw=3, draws_per_week=3,
                     weeks=52, n_years=40, seed=100 + i)
    assert r.lose_probability > 0.5


def test_expected_profit_negative():
    """负期望：预计盈亏应为负。"""
    r = analyze_risk(cost_per_note=2, notes_per_draw=1, draws_per_week=3,
                     weeks=52, n_years=N)
    assert r.expected_profit < 0


# ---------- 报告结构 ----------
def test_report_type():
    r = analyze_risk(n_years=N)
    assert isinstance(r, RiskReport)


def test_report_fields():
    r = analyze_risk(n_years=N)
    for f in ("annual_draws", "annual_investment", "max_loss",
              "expected_return", "lose_probability", "risk_level"):
        assert hasattr(r, f)


@pytest.mark.parametrize("f", ["annual_investment", "max_loss",
                               "expected_return", "lose_probability", "risk_level"])
def test_report_dict_keys(f):
    r = analyze_risk(n_years=N)
    assert f in r.to_dict()


def test_summary_text_fields():
    r = analyze_risk(n_years=N)
    t = r.summary_text()
    for kw in ("年度投入", "最大损失", "预计回报", "亏损概率", "风险等级"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer():
    r = analyze_risk(n_years=N)
    assert "负期望" in r.disclaimer or "理性购彩" in r.disclaimer
    assert "预测" not in r.disclaimer


def test_summary_has_disclaimer():
    r = analyze_risk(n_years=N)
    assert "理性购彩" in r.summary_text()


# ---------- 双色球 ----------
@pytest.mark.parametrize("i", range(10))
def test_ssq_risk(i):
    r = analyze_risk(cost_per_note=2, notes_per_draw=2, draws_per_week=3,
                     weeks=52, lottery="ssq", n_years=40, seed=i)
    assert r.lottery == "ssq"
    assert r.lottery_name == "双色球"
    assert 0 <= r.lose_probability <= 1


# ---------- tickets 参数 ----------
def test_tickets_notes_override():
    tickets = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]} for _ in range(15)]
    r = analyze_risk(cost_per_note=2, notes_per_draw=1, draws_per_week=3,
                     weeks=52, tickets=tickets, n_years=N)
    assert r.notes_per_draw == 15
    assert r.annual_investment == 2 * 15 * 3 * 52


def test_tickets_empty_uses_notes():
    r = analyze_risk(cost_per_note=2, notes_per_draw=5, draws_per_week=3,
                     weeks=52, tickets=[], n_years=N)
    assert r.notes_per_draw == 5


# ---------- 参数化大规模 ----------
@pytest.mark.parametrize("cost,notes,draws,weeks", [
    (2, 1, 1, 1), (2, 1, 1, 26), (2, 1, 1, 52), (2, 1, 3, 52),
    (2, 5, 3, 52), (2, 10, 3, 52), (2, 15, 3, 52), (2, 30, 1, 52),
    (5, 1, 3, 52), (10, 1, 3, 52), (2, 2, 2, 2), (2, 8, 4, 12),
])
def test_param_matrix(cost, notes, draws, weeks):
    r = analyze_risk(cost_per_note=cost, notes_per_draw=notes,
                     draws_per_week=draws, weeks=weeks, n_years=N)
    assert r.annual_investment == cost * notes * draws * weeks
    assert r.risk_level in ("A", "B", "C", "D")
    assert r.lose_probability >= 0


@pytest.mark.parametrize("seed", range(20))
def test_seed_determinism(seed):
    a = analyze_risk(cost_per_note=2, notes_per_draw=3, draws_per_week=3,
                     weeks=52, n_years=40, seed=seed)
    b = analyze_risk(cost_per_note=2, notes_per_draw=3, draws_per_week=3,
                     weeks=52, n_years=40, seed=seed)
    assert a.to_dict() == b.to_dict()
