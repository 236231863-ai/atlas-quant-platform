"""v3.8.2-P1 Phase 3：PrizeCalculator 真实大乐透/双色球规则验证。"""
from __future__ import annotations

import random

import pytest

from engine.lottery_intent.prize_calculator import PrizeCalculator

# 大乐透：(前区命中, 后区命中) → (等级, 固定奖金)
DLT_CASES = [
    ((5, 2), "一等奖", 5_000_000),
    ((5, 1), "二等奖", 180_000),
    ((5, 0), "三等奖", 10_000),
    ((4, 2), "四等奖", 3_000),
    ((4, 1), "五等奖", 300),
    ((3, 2), "六等奖", 200),
    ((4, 0), "七等奖", 100),
    ((3, 1), "八等奖", 15),
    ((2, 2), "八等奖", 15),
    ((3, 0), "九等奖", 5),
    ((1, 2), "九等奖", 5),
    ((2, 1), "九等奖", 5),
    ((0, 2), "九等奖", 5),
]

# 双色球：(红球, 蓝球) → (等级, 固定奖金)
SSQ_CASES = [
    ((6, 1), "一等奖", 5_000_000),
    ((6, 0), "二等奖", 100_000),
    ((5, 1), "三等奖", 3_000),
    ((5, 0), "四等奖", 200),
    ((4, 1), "四等奖", 200),
    ((4, 0), "五等奖", 10),
    ((3, 1), "五等奖", 10),
    ((2, 1), "六等奖", 5),
    ((1, 1), "六等奖", 5),
    ((0, 1), "六等奖", 5),
]


@pytest.mark.parametrize("hits,level,amount", DLT_CASES)
def test_dlt_rule_table(hits, level, amount):
    r = PrizeCalculator.calculate(*hits, "dlt")
    assert r.prize_level == level, f"{hits} 应为 {level}"
    assert r.amount == amount, f"{hits} 奖金应为 {amount}"


@pytest.mark.parametrize("hits,level,amount", SSQ_CASES)
def test_ssq_rule_table(hits, level, amount):
    r = PrizeCalculator.calculate(*hits, "ssq")
    assert r.prize_level == level
    assert r.amount == amount


@pytest.mark.parametrize("hits", [(0, 0), (1, 1), (0, 1), (1, 0), (2, 0)])
def test_dlt_no_win(hits):
    r = PrizeCalculator.calculate(*hits, "dlt")
    assert not r.won
    assert r.prize_level is None
    assert r.amount == 0


# 全命中矩阵：front 0-5 × back 0-2
_ALL_HITS = [(fh, bh) for fh in range(6) for bh in range(3)]


@pytest.mark.parametrize("fh,bh", _ALL_HITS)
def test_dlt_all_hit_matrix(fh, bh):
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    if r.won:
        assert r.amount >= 5
        assert r.prize_level is not None
    else:
        assert r.amount == 0


# ---------- 15 注逐注匹配（真实开奖 26086 期：10 11 18 22 35 + 06 12）----------
DRAW_FRONT = {10, 11, 18, 22, 35}
DRAW_BACK = {6, 12}

FIFTEEN_NOTES = [
    ([10, 11, 18, 22, 35], [6, 12], "一等奖", 5_000_000),
    ([10, 11, 18, 22, 35], [6, 1], "二等奖", 180_000),
    ([10, 11, 18, 22, 35], [1, 2], "三等奖", 10_000),
    ([10, 11, 18, 22, 1], [6, 12], "四等奖", 3_000),
    ([10, 11, 18, 22, 1], [6, 7], "五等奖", 300),
    ([10, 11, 18, 1, 2], [6, 12], "六等奖", 200),
    ([10, 11, 18, 22, 1], [7, 8], "七等奖", 100),
    ([10, 11, 18, 1, 2], [6, 7], "八等奖", 15),
    ([10, 11, 1, 2, 3], [6, 12], "八等奖", 15),
    ([10, 11, 18, 1, 2], [7, 8], "九等奖", 5),
    ([10, 1, 2, 3, 4], [6, 12], "九等奖", 5),
    ([10, 11, 1, 2, 3], [6, 7], "九等奖", 5),
    ([1, 2, 3, 4, 5], [6, 12], "九等奖", 5),
    ([1, 2, 3, 4, 5], [7, 8], None, 0),
    ([10, 1, 2, 3, 4], [6, 7], None, 0),
]


@pytest.mark.parametrize("front,back,level,amount", FIFTEEN_NOTES)
def test_fifteen_notes_prize(front, back, level, amount):
    """15 注逐注匹配：号码 → 命中 → 等级 → 奖金。"""
    fh = len(set(front) & DRAW_FRONT)
    bh = len(set(back) & DRAW_BACK)
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    assert r.prize_level == level
    assert r.amount == amount


def test_fifteen_notes_total():
    """15 注总奖金 = 5,193,650。"""
    total = 0
    won = 0
    for front, back, level, amount in FIFTEEN_NOTES:
        fh = len(set(front) & DRAW_FRONT)
        bh = len(set(back) & DRAW_BACK)
        r = PrizeCalculator.calculate(fh, bh, "dlt")
        total += r.amount
        if r.won:
            won += 1
    assert total == 5_193_650
    assert won == 13


# ---------- 100 组随机命中验证 ----------
@pytest.fixture(scope="module")
def random_hit_cases():
    rng = random.Random(826)
    out = []
    for _ in range(100):
        fh = rng.randint(0, 5)
        bh = rng.randint(0, 2)
        out.append((fh, bh))
    return out


@pytest.mark.parametrize("idx", list(range(100)))
def test_random_hit_matrix(idx, random_hit_cases):
    fh, bh = random_hit_cases[idx]
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    # 规则一致性：命中数与金额非负
    assert r.amount >= 0
    assert 0 <= r.front_hit <= 5
    assert 0 <= r.back_hit <= 2
    if r.won:
        assert r.amount >= 5
        assert r.prize_level in {"一等奖", "二等奖", "三等奖", "四等奖",
                                 "五等奖", "六等奖", "七等奖", "八等奖", "九等奖"}
    else:
        assert r.prize_level is None


# ---------- total_for 汇总 ----------
def test_total_for_summary():
    matches = []
    for front, back, level, amount in FIFTEEN_NOTES:
        class _M:
            front_hits = len(set(front) & DRAW_FRONT)
            back_hits = len(set(back) & DRAW_BACK)
        matches.append(_M())
    summary = PrizeCalculator.total_for(matches, "dlt")
    assert summary["total"] == 5_193_650
    assert summary["won_notes"] == 13
    assert len(summary["details"]) == 15


def test_total_for_empty():
    summary = PrizeCalculator.total_for([], "dlt")
    assert summary["total"] == 0
    assert summary["won_notes"] == 0
    assert summary["details"] == []
