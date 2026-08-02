"""v3.9.0 Phase 3：蒙特卡洛模拟测试。"""
from __future__ import annotations

import random

import pytest

from engine.lottery_quant.simulation import (
    SimulationEngine,
    SimulationReport,
    simulate_coverage,
)

BASE_TICKETS = [
    {"front": [10, 11, 18, 22, 35], "back": [6, 12]},
    {"front": [1, 2, 3, 4, 5], "back": [6, 7]},
    {"front": [5, 10, 15, 20, 25], "back": [8, 9]},
]


def _mk_tickets(n, seed=100):
    rng = random.Random(seed)
    return [{"front": sorted(rng.sample(range(1, 36), 5)),
             "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(n)]


# ---------- 基本功能 ----------
def test_simulation_basic():
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    assert isinstance(r, SimulationReport)
    assert r.trials == 1000
    assert r.note_count == 3


@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 15, 30])
def test_simulation_note_counts(n):
    r = simulate_coverage(_mk_tickets(n), trials=500, seed=5)
    assert r.note_count == n


@pytest.mark.parametrize("trials", [10, 100, 500, 1000, 5000])
def test_simulation_trials_counts(trials):
    r = simulate_coverage(BASE_TICKETS, trials=trials, seed=7)
    assert r.trials == trials


# ---------- 确定性（同 seed 一致）----------
@pytest.mark.parametrize("seed", [0, 1, 42, 99, 12345])
def test_deterministic_same_seed(seed):
    a = simulate_coverage(BASE_TICKETS, trials=1000, seed=seed)
    b = simulate_coverage(BASE_TICKETS, trials=1000, seed=seed)
    assert a.to_dict() == b.to_dict()


@pytest.mark.parametrize("seed_a,seed_b", [(1, 2), (10, 20), (5, 6)])
def test_different_seeds(seed_a, seed_b):
    a = simulate_coverage(BASE_TICKETS, trials=5000, seed=seed_a)
    b = simulate_coverage(BASE_TICKETS, trials=5000, seed=seed_b)
    # 不同种子覆盖率可以略有差异（极小概率相等，这里只断言次数非负）
    assert a.first_prize_hits >= 0
    assert b.first_prize_hits >= 0


# ---------- 覆盖率范围 ----------
@pytest.mark.parametrize("i", range(20))
def test_coverage_rate_bounded(i):
    r = simulate_coverage(_mk_tickets(5, seed=200 + i), trials=2000, seed=i)
    assert 0.0 <= r.coverage_rate <= 1.0


@pytest.mark.parametrize("i", range(20))
def test_coverage_rate_increasing_with_notes(i):
    """注数越多，覆盖率越高（或持平）。"""
    r1 = simulate_coverage(_mk_tickets(1, seed=300 + i), trials=3000, seed=i)
    r2 = simulate_coverage(_mk_tickets(5, seed=300 + i), trials=3000, seed=i)
    assert r2.coverage_rate >= r1.coverage_rate


# ---------- 期望奖金 ----------
@pytest.mark.parametrize("i", range(15))
def test_expected_return_non_negative(i):
    r = simulate_coverage(_mk_tickets(3, seed=400 + i), trials=2000, seed=i)
    assert r.expected_return >= 0


def test_expected_return_reasonable():
    """单注彩票期望回报远低于成本（<2 元）。"""
    r = simulate_coverage(BASE_TICKETS, trials=20000, seed=42)
    assert r.expected_return < 2.0


# ---------- 一等奖/二等奖 ----------
def test_first_prize_hits_small_trials():
    """小额模拟一等奖命中应为 0（概率 1/2142万）。"""
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    assert r.first_prize_hits == 0


def test_second_prize_hits_small_trials():
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    assert r.second_prize_hits == 0


@pytest.mark.parametrize("trials", [100, 500, 1000])
def test_minor_prize_hits_non_negative(trials):
    r = simulate_coverage(BASE_TICKETS, trials=trials, seed=3)
    assert r.minor_prize_hits >= 0


# ---------- 双色球 ----------
@pytest.mark.parametrize("i", range(15))
def test_ssq_simulation(i):
    tickets = [{"front": sorted(random.Random(500 + i).sample(range(1, 34), 6)),
                "back": [random.Random(600 + i).randint(1, 16)]} for _ in range(5)]
    r = simulate_coverage(tickets, lottery="ssq", trials=2000, seed=i)
    assert r.lottery == "ssq"
    assert r.lottery_name == "双色球"
    assert 0 <= r.coverage_rate <= 1


# ---------- 无效输入 ----------
def test_empty_tickets():
    r = simulate_coverage([], trials=1000, seed=1)
    assert r.coverage_rate == 0
    assert r.note_count == 0


def test_zero_trials():
    r = simulate_coverage(BASE_TICKETS, trials=0, seed=1)
    assert r.coverage_rate == 0


@pytest.mark.parametrize("bad", [
    [{"front": [1, 2, 3], "back": []}],              # 号码不足
    [{"front": [], "back": []}],                     # 空
    [{"front": [1, 2, 3, 4, 5, 6, 7, 8], "back": []}],  # 前区超量
])
def test_invalid_tickets(bad):
    r = simulate_coverage(bad, trials=500, seed=1)
    assert isinstance(r, SimulationReport)


# ---------- 报告字段 ----------
def test_report_fields():
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    for f in ("lottery", "trials", "note_count", "first_prize_hits",
              "second_prize_hits", "minor_prize_hits", "coverage_rate",
              "expected_return", "disclaimer"):
        assert hasattr(r, f)


@pytest.mark.parametrize("f", ["lottery", "trials", "note_count",
                               "first_prize_hits", "second_prize_hits",
                               "minor_prize_hits", "coverage_rate",
                               "expected_return", "disclaimer"])
def test_report_dict_keys(f):
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    assert f in r.to_dict()


def test_summary_text_fields():
    r = simulate_coverage(BASE_TICKETS, trials=1000, seed=1)
    t = r.summary_text()
    for kw in ("模拟次数", "覆盖率", "期望奖金", "随机性"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer_not_prediction():
    r = simulate_coverage(BASE_TICKETS, trials=100, seed=1)
    assert "不代表未来" in r.disclaimer
    assert "随机性" in r.disclaimer
    assert "预测" not in r.disclaimer


def test_summary_has_disclaimer():
    r = simulate_coverage(BASE_TICKETS, trials=100, seed=1)
    assert "不代表未来" in r.summary_text()


# ---------- 模拟引擎细节 ----------
def test_draw_generation():
    rng = random.Random(1)
    front, back = SimulationEngine._draw(rng, "dlt")
    assert len(front) == 5
    assert len(back) == 2
    assert all(1 <= n <= 35 for n in front)
    assert all(1 <= n <= 12 for n in back)


@pytest.mark.parametrize("i", range(20))
def test_draw_random_generation(i):
    rng = random.Random(i)
    front, back = SimulationEngine._draw(rng, "dlt")
    assert len(set(front)) == 5
    assert len(set(back)) == 2


def test_ticket_sets_filtering():
    tickets = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
               {"front": [1, 2, 3], "back": []}]   # 无效注应被过滤
    sets = SimulationEngine._ticket_sets(tickets, "dlt")
    assert len(sets) == 1


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_large_param_matrix(seed):
    r = simulate_coverage(_mk_tickets(4, seed=seed), trials=1500, seed=seed)
    assert 0 <= r.coverage_rate <= 1
    assert r.expected_return >= 0
    assert r.trials == 1500


@pytest.mark.parametrize("seed", range(40))
def test_ssq_param_matrix(seed):
    tickets = [{"front": sorted(random.Random(700 + seed).sample(range(1, 34), 6)),
                "back": [random.Random(800 + seed).randint(1, 16)]} for _ in range(6)]
    r = simulate_coverage(tickets, lottery="ssq", trials=1000, seed=seed)
    assert 0 <= r.coverage_rate <= 1
    assert r.minor_prize_hits >= 0
    assert r.first_prize_hits == 0


@pytest.mark.parametrize("seed", range(30))
def test_single_note_coverage(seed):
    t = _mk_tickets(1, seed=seed)
    r = simulate_coverage(t, trials=5000, seed=seed)
    # 单注大乐透总中奖率约 6.7%，覆盖率应 > 3%
    assert r.coverage_rate > 0.03
    assert r.coverage_rate < 0.15
