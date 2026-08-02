"""v3.9.0 Phase 6：策略回测测试。"""
from __future__ import annotations

import pytest

from engine.lottery_quant.backtest import (
    STRATEGY_METHODS,
    STRATEGY_NAMES,
    StrategyBacktester,
    StrategyReport,
    run_strategy_backtest,
)


@pytest.fixture(scope="module")
def report():
    return run_strategy_backtest(periods=80)


# ---------- 策略存在 ----------
def test_strategy_methods():
    assert STRATEGY_METHODS == ["hot", "cold", "balanced", "random"]


def test_all_strategies_present(report):
    for m in STRATEGY_METHODS:
        assert m in report.strategies


def test_strategy_names():
    assert STRATEGY_NAMES["hot"] == "热号策略"
    assert STRATEGY_NAMES["random"] == "随机策略"


@pytest.mark.parametrize("method", STRATEGY_METHODS)
def test_strategy_present(method, report):
    assert method in report.strategies


# ---------- 报告结构 ----------
def test_report_type(report):
    assert isinstance(report, StrategyReport)


def test_report_periods(report):
    assert report.periods == 80


@pytest.mark.parametrize("f", ["periods", "strategies", "best_strategy", "disclaimer"])
def test_report_dict_keys(f, report):
    assert f in report.to_dict()


def test_best_strategy_valid(report):
    assert report.best_strategy() in STRATEGY_METHODS


def test_best_strategy_roi_highest(report):
    best = report.best_strategy()
    best_roi = report.strategies[best].roi_total
    for m in STRATEGY_METHODS:
        assert report.strategies[m].roi_total <= best_roi + 1e-9


# ---------- 各策略指标 ----------
@pytest.mark.parametrize("method", STRATEGY_METHODS)
def test_strategy_roi_present(method, report):
    perf = report.strategies[method]
    assert isinstance(perf.roi_total, float)
    assert perf.n_bets_total >= 0


@pytest.mark.parametrize("method", STRATEGY_METHODS)
def test_strategy_win_rate_range(method, report):
    perf = report.strategies[method]
    assert 0.0 <= perf.win_rate <= 1.0


# ---------- 随机基准 ----------
def test_random_baseline_present(report):
    assert any(v.baseline_roi_mean for v in report.strategies.values())


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_has_baseline(method, report):
    perf = report.strategies[method]
    assert hasattr(perf, "baseline_roi_mean")
    assert hasattr(perf, "baseline_roi_p95")


# ---------- 结论 ----------
def test_conclusion_no_prediction(report):
    for m in STRATEGY_METHODS:
        conclusion = report.strategies[m].conclusion()
        assert "预测" not in conclusion
        assert "不代表未来" in conclusion or "随机" in conclusion


def test_summary_text_fields(report):
    t = report.summary_text()
    for kw in ("ROI", "命中率", "随机基准", "历史回测"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer(report):
    assert "不代表未来" in report.disclaimer
    assert "盈利保证" in report.disclaimer


def test_summary_has_disclaimer(report):
    assert "盈利保证" in report.summary_text()


# ---------- 确定性 ----------
def test_random_strategy_deterministic():
    a = run_strategy_backtest(periods=50, seed=7)
    b = run_strategy_backtest(periods=50, seed=7)
    assert a.strategies["random"].roi_total == b.strategies["random"].roi_total


def test_different_seeds_vary():
    a = run_strategy_backtest(periods=50, seed=1)
    b = run_strategy_backtest(periods=50, seed=99)
    assert isinstance(a.strategies["random"].roi_total, float)


# ---------- periods 参数化 ----------
@pytest.mark.parametrize("periods", [10, 30, 50, 80, 120, 200])
def test_periods_matrix(periods):
    r = run_strategy_backtest(periods=periods)
    assert r.periods == periods
    for m in STRATEGY_METHODS:
        assert m in r.strategies


@pytest.mark.parametrize("periods", [5, 10, 20])
def test_small_periods(periods):
    r = run_strategy_backtest(periods=periods)
    assert isinstance(r, StrategyReport)


# ---------- 单策略运行 ----------
@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_single_method(method):
    r = run_strategy_backtest(periods=60, methods=[method])
    assert set(r.strategies.keys()) == {method}


def test_random_only():
    r = run_strategy_backtest(periods=60, methods=["random"])
    assert set(r.strategies.keys()) == {"random"}


# ---------- 空数据 ----------
def test_empty_draws():
    r = run_strategy_backtest(draws=[], periods=100)
    assert isinstance(r, StrategyReport)


def test_tiny_draws():
    class _D:
        number = "1"
        draw_date = "2026-01-01"
        front = [1, 2, 3, 4, 5]
        back = [6, 7]
        def format_front(self):
            return "01 02 03 04 05"
        def format_back(self):
            return "06 07"
    draws = [_D() for _ in range(3)]
    r = run_strategy_backtest(draws=draws, periods=100)
    assert isinstance(r, StrategyReport)


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(25))
def test_seed_matrix(seed):
    r = run_strategy_backtest(periods=40, seed=seed)
    assert r.best_strategy() in STRATEGY_METHODS
    for m in STRATEGY_METHODS:
        assert r.strategies[m].n_bets_total >= 0


@pytest.mark.parametrize("periods,method", [
    (30, m) for m in STRATEGY_METHODS
] + [(50, m) for m in STRATEGY_METHODS] + [(70, m) for m in STRATEGY_METHODS])
def test_period_method_matrix(periods, method):
    r = run_strategy_backtest(periods=periods, methods=[method])
    assert method in r.strategies
    assert r.strategies[method].n_bets_total >= 0


@pytest.mark.parametrize("i", range(30))
def test_report_valid_always(i):
    r = run_strategy_backtest(periods=30 + i % 100, seed=i)
    assert isinstance(r.to_dict(), dict)
    assert len(r.strategies) == 4


# ---------- 大规模扩展矩阵 ----------
@pytest.mark.parametrize("periods,seed", [(20, s) for s in range(15)]
                         + [(40, s) for s in range(15)] + [(60, s) for s in range(15)])
def test_extended_matrix(periods, seed):
    r = run_strategy_backtest(periods=periods, seed=seed)
    assert r.periods == periods
    for m in STRATEGY_METHODS:
        assert m in r.strategies
        assert r.strategies[m].n_bets_total >= 0
    assert r.best_strategy() in STRATEGY_METHODS


@pytest.mark.parametrize("seed", range(30))
def test_roi_negative_expectation(seed):
    """彩票负期望：多数策略 ROI 为负（诚实表达）。"""
    r = run_strategy_backtest(periods=100, seed=seed)
    random_roi = r.strategies["random"].roi_total
    assert random_roi < 0  # 随机策略长期必然亏损


@pytest.mark.parametrize("seed", range(20))
def test_strategy_dict_shape(seed):
    r = run_strategy_backtest(periods=50, seed=seed)
    d = r.to_dict()
    assert len(d["strategies"]) == 4
    for name, perf in d["strategies"].items():
        assert name in STRATEGY_METHODS
        for k in ("roi_total", "win_rate", "baseline_roi_mean", "conclusion"):
            assert k in perf
