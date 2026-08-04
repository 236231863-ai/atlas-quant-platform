"""v4.7 P4：策略复盘系统测试。

覆盖：固定/随机/倍投/重复比例/冷热 / 禁「下一期怎么买」。
"""
from __future__ import annotations

import pytest

from engine.strategy_review import (
    StrategyReview, StrategyReviewer, build_strategy_review,
)


def combo(front, back, tid="T"):
    return {"ticket_id": tid, "lottery": "dlt", "front": list(front),
            "back": list(back), "buy_date": "2026-08-01",
            "draw_date": "2026-08-01", "cost": 2.0}


FIXED = [1, 2, 3, 4, 5]
RANDOM = [11, 12, 13, 14, 15]
BACK = [1, 2]


# ---------- 固定/随机 ----------
def test_empty():
    r = build_strategy_review([])
    assert r.total_tickets == 0


def test_all_unique():
    tickets = [combo(list(range(1 + i, 6 + i)), [1, 2], f"T{i}") for i in range(5)]
    r = build_strategy_review(tickets)
    assert r.unique_combos == 5
    assert r.random_count == 5
    assert r.fixed_combo_count == 0
    assert r.repeat_ratio == 0.0


def test_fixed_combo():
    tickets = [combo(FIXED, BACK, f"T{i}") for i in range(3)]
    r = build_strategy_review(tickets)
    assert r.fixed_combo_count == 1
    assert r.random_count == 0
    assert r.doubled_times == 2
    assert r.repeat_ratio == 1.0


def test_mixed():
    tickets = [combo(FIXED, BACK, "T1"), combo(FIXED, BACK, "T2"),
               combo(RANDOM, BACK, "T3")]
    r = build_strategy_review(tickets)
    assert r.unique_combos == 2
    assert r.fixed_combo_count == 1
    assert r.random_count == 1
    assert r.doubled_times == 1
    assert r.repeat_ratio == 0.5


# ---------- 冷热 ----------
def test_hot_cold_use():
    tickets = [combo([1, 2, 3, 4, 5], [1, 2], "T1"),
               combo([1, 2, 3, 4, 5], [1, 2], "T2"),
               combo([10, 11, 12, 13, 14], [1, 2], "T3"),
               combo([20, 21, 22, 23, 24], [1, 2], "T4")]
    r = build_strategy_review(tickets)
    assert r.hot_use >= 1  # 1/2 是热号


# ---------- 结构 ----------
def test_summary_text():
    r = build_strategy_review([combo(FIXED, BACK)])
    assert "策略复盘" in r.summary_text()
    assert "随机性" in r.summary_text()


def test_no_next_advice():
    """禁止「下一期怎么买」。"""
    r = build_strategy_review([combo(FIXED, BACK)])
    assert "下一期" not in r.summary_text()


def test_to_dict():
    r = build_strategy_review([combo(FIXED, BACK)])
    d = r.to_dict()
    assert "repeat_ratio" in d
    assert "doubled_times" in d


def test_disclaimer():
    assert "随机性" in StrategyReview().disclaimer


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_ticket_scale(n):
    """每张票号码不同 → 全部唯一组合。"""
    tickets = [combo(list(range(1 + i, 6 + i)), [1, 2], f"T{i}") for i in range(n)]
    r = build_strategy_review(tickets)
    assert r.total_tickets == n
    assert r.unique_combos == n
    assert r.random_count == n


@pytest.mark.parametrize("dup", [1, 2, 3])
def test_duplicate_scale(dup):
    tickets = [combo(FIXED, BACK, f"T{i}") for i in range(dup)]
    r = build_strategy_review(tickets)
    if dup == 1:
        assert r.fixed_combo_count == 0
        assert r.doubled_times == 0
    else:
        assert r.fixed_combo_count == 1
        assert r.doubled_times == dup - 1


@pytest.mark.parametrize("seed", range(10))
def test_random(seed):
    import random
    random.seed(seed)
    tickets = []
    for i in range(random.randint(1, 10)):
        front = random.sample(range(1, 36), 5)
        tickets.append(combo(front, [random.randint(1, 12), random.randint(1, 12)], f"T{i}"))
    r = build_strategy_review(tickets)
    assert r.total_tickets == len(tickets)
    assert 0.0 <= r.repeat_ratio <= 1.0
    assert r.summary_text()
