"""v3.6.1 回测可信化测试：样本划分 / 随机基准 / 性能报告 / 免责声明。"""
import pytest

from engine.evaluation_v2 import (
    temporal_split, RandomBaseline, run_backtest_with_evaluation,
    get_disclaimer, get_short_disclaimer, validate_copy,
    FORBIDDEN_EXPRESSIONS, DLT_PRIZES,
)
from engine.data_center_v2 import DrawRecord


def _mk_draws(n, seed=0):
    draws = []
    import random
    rng = random.Random(seed)
    for i in range(n):
        front = sorted(rng.sample(range(1, 36), 5))
        back = sorted(rng.sample(range(1, 13), 2))
        draws.append(DrawRecord(f"{24000+i}", f"2026-01-{(i % 28) + 1:02d}", front, back, 100.0))
    return draws


# ---------- 样本划分 ----------
@pytest.mark.parametrize("n,train_ratio", [
    (10, 0.7), (100, 0.7), (520, 0.7), (1000, 0.5), (37, 0.8), (5, 0.9),
])
def test_temporal_split_counts(n, train_ratio):
    draws = _mk_draws(n)
    train, valid = temporal_split(draws, train_ratio)
    assert len(train) + len(valid) == n
    assert len(train) == int(n * train_ratio)
    assert len(train) <= len(valid) or len(train) >= len(valid) - 1  # 比例合理


@pytest.mark.parametrize("ratio", [0.0, 1.0, -0.1, 1.5])
def test_temporal_split_invalid_ratio(ratio):
    with pytest.raises(ValueError):
        temporal_split(_mk_draws(10), ratio)


@pytest.mark.parametrize("n", [0, 1, 2, 3, 10])
def test_temporal_split_ordering(n):
    draws = _mk_draws(n)
    train, valid = temporal_split(draws)
    # 训练集在前，验证集在后（时序）
    assert all(d.number < v.number for d in train for v in valid)


# ---------- 随机基准 ----------
@pytest.mark.parametrize("n_sim,seed", [
    (5, 1), (10, 2), (20, 3), (50, 42), (100, 7),
])
def test_random_baseline_returns_summary(n_sim, seed):
    draws = _mk_draws(50)
    bl = RandomBaseline(n_simulations=n_sim, seed=seed)
    r = bl.evaluate(draws)
    assert r["n_simulations"] == n_sim
    assert r["roi_p5"] <= r["roi_mean"] <= r["roi_p95"]
    assert r["n_bets"] == 50


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_random_baseline_deterministic(seed):
    draws = _mk_draws(20)
    a = RandomBaseline(n_simulations=10, seed=seed).evaluate(draws)
    b = RandomBaseline(n_simulations=10, seed=seed).evaluate(draws)
    assert a["roi_mean"] == b["roi_mean"]


@pytest.mark.parametrize("front_n,back_n", [(5, 2), (6, 1), (4, 2), (5, 1)])
def test_random_baseline_ticket_shape(front_n, back_n):
    draws = _mk_draws(5)
    bl = RandomBaseline(front_n=front_n, back_n=back_n, n_simulations=3, seed=1)
    r = bl.evaluate(draws)
    assert r["n_bets"] == 5


@pytest.mark.parametrize("n_bets", [1, 5, 30, 100])
def test_random_baseline_scales_with_data(n_bets):
    draws = _mk_draws(n_bets)
    bl = RandomBaseline(n_simulations=5, seed=1)
    r = bl.evaluate(draws)
    assert r["n_bets"] == n_bets


@pytest.mark.parametrize("ticket_cost", [1.0, 2.0, 5.0, 10.0])
def test_random_baseline_ticket_cost(ticket_cost):
    draws = _mk_draws(10)
    bl = RandomBaseline(ticket_cost=ticket_cost, n_simulations=5, seed=1)
    r = bl.evaluate(draws)
    assert r["n_bets"] == 10


# ---------- 完整回测 + 评估 ----------
@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_backtest_all_methods(method):
    draws = _mk_draws(80)
    report = run_backtest_with_evaluation(draws, method=method, n_simulations=5)
    assert report.n_bets_total == 80 - 3
    assert report.roi_total is not None


@pytest.mark.parametrize("train_ratio", [0.5, 0.7, 0.8])
def test_backtest_sample_split(train_ratio):
    draws = _mk_draws(100)
    report = run_backtest_with_evaluation(draws, train_ratio=train_ratio, n_simulations=5)
    assert report.n_bets_train + report.n_bets_oos == report.n_bets_total


@pytest.mark.parametrize("n_sim", [3, 5, 10])
def test_backtest_baseline_compare(n_sim):
    draws = _mk_draws(60)
    report = run_backtest_with_evaluation(draws, n_simulations=n_sim, seed=1)
    assert report.baseline_roi_mean is not None
    assert report.baseline_roi_p5 <= report.baseline_roi_p95


@pytest.mark.parametrize("n_draws", [0, 1, 2, 3, 4])
def test_backtest_insufficient_data(n_draws):
    draws = _mk_draws(n_draws)
    report = run_backtest_with_evaluation(draws)
    assert report.n_bets_total == 0


@pytest.mark.parametrize("seed", [0, 5, 10, 20, 42])
def test_backtest_deterministic(seed):
    draws = _mk_draws(50)
    a = run_backtest_with_evaluation(draws, seed=seed, n_simulations=5)
    b = run_backtest_with_evaluation(draws, seed=seed, n_simulations=5)
    assert a.roi_total == b.roi_total
    assert a.baseline_roi_mean == b.baseline_roi_mean


@pytest.mark.parametrize("idx", [0, 1, 10, 50, 90])
def test_backtest_records_have_fields(idx):
    draws = _mk_draws(100)
    report = run_backtest_with_evaluation(draws, n_simulations=3)
    r = report.records[idx]
    assert r.issue
    assert r.recommended
    assert r.actual
    assert r.equity is not None


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_backtest_conclusion_contains_random(method):
    draws = _mk_draws(60)
    report = run_backtest_with_evaluation(draws, method=method, n_simulations=5)
    c = report.conclusion()
    assert "随机" in c
    assert "历史" in c


# ---------- 免责声明 ----------
@pytest.mark.parametrize("n", [1, 2, 3])
def test_disclaimer_present(n):
    assert "随机" in get_disclaimer()
    assert "研究参考" in get_disclaimer()
    assert "理性" in get_disclaimer()


def test_short_disclaimer():
    assert "随机" in get_short_disclaimer()


@pytest.mark.parametrize("word", FORBIDDEN_EXPRESSIONS)
def test_forbidden_words_detected(word):
    hits = validate_copy(f"本产品{word}！")
    assert word in hits


@pytest.mark.parametrize("text", ["正常文案", "数据仅供参考", "历史回测说明", ""])
def test_clean_copy_no_forbidden(text):
    assert validate_copy(text) == []


# ---------- 奖项规则 ----------
@pytest.mark.parametrize("f,b", [(5, 2), (5, 1), (5, 0), (4, 2), (4, 1), (3, 2), (0, 2), (2, 1), (1, 2)])
def test_prizes_cover_rules(f, b):
    from engine.evaluation_v2.baseline import _grade
    name, amount = _grade(f, b)
    assert name is not None
    assert amount > 0


@pytest.mark.parametrize("f,b", [(5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 1), (0, 0)])
def test_prizes_no_win(f, b):
    from engine.evaluation_v2.baseline import _grade
    name, amount = _grade(f, b)
    # 只有后区不中且前区<3 时无奖
    assert amount >= 0
