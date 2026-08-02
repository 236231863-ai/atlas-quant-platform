"""v3.9.0 Phase 2：号码结构分析器测试。"""
from __future__ import annotations

import random

import pytest

from engine.lottery_quant.structure import (
    StructureAnalyzer,
    StructureMetrics,
    CombinationScore,
    analyze_combination,
)

# ---------- 奇偶 ----------
ODD_EVEN_CASES = [
    ([1, 3, 5, 7, 9], (5, 0)),
    ([2, 4, 6, 8, 10], (0, 5)),
    ([1, 2, 3, 4, 5], (3, 2)),
    ([1, 2, 3, 4, 6], (2, 3)),
    ([1, 2, 4, 6, 8], (1, 4)),
    ([1, 3, 5, 7, 8], (4, 1)),
    ([2, 4, 6, 8, 9], (1, 4)),
    ([11, 12, 13, 14, 15], (3, 2)),
    ([21, 22, 23, 24, 25], (3, 2)),
    ([10, 11, 18, 22, 35], (2, 3)),
    ([1, 8, 15, 22, 30], (2, 3)),
    ([2, 3, 4, 14, 28], (1, 4)),
    ([5, 10, 15, 20, 25], (3, 2)),
    ([3, 4, 14, 28, 31], (2, 3)),
    ([13, 25, 30, 32, 33], (3, 2)),
]


@pytest.mark.parametrize("front,expected", ODD_EVEN_CASES)
def test_odd_even(front, expected):
    assert StructureAnalyzer.odd_even(front) == expected


# ---------- 大小（≥18 为大）----------
BIG_SMALL_CASES = [
    ([1, 3, 5, 7, 9], (0, 5)),
    ([18, 19, 20, 21, 22], (5, 0)),
    ([1, 2, 17, 18, 19], (2, 3)),
    ([10, 11, 18, 22, 35], (3, 2)),
    ([1, 8, 15, 22, 30], (2, 3)),
    ([2, 3, 4, 14, 28], (1, 4)),
    ([1, 2, 3, 4, 5], (0, 5)),
    ([13, 25, 30, 32, 33], (4, 1)),
    ([10, 11, 12, 13, 14], (0, 5)),
    ([20, 22, 24, 26, 28], (5, 0)),
    ([2, 4, 6, 8, 10], (0, 5)),
    ([20, 22, 24, 26, 28], (5, 0)),
]


@pytest.mark.parametrize("front,expected", BIG_SMALL_CASES)
def test_big_small(front, expected):
    assert StructureAnalyzer.big_small(front) == expected


# ---------- 三区（1-12/13-24/25-35）----------
ZONE_CASES = [
    ([1, 3, 5, 7, 9], (5, 0, 0)),
    ([13, 15, 17, 19, 21], (0, 5, 0)),
    ([25, 27, 29, 31, 33], (0, 0, 5)),
    ([1, 13, 25, 30, 35], (1, 1, 3)),
    ([10, 11, 18, 22, 35], (2, 2, 1)),
    ([1, 8, 15, 22, 30], (2, 2, 1)),
    ([2, 3, 4, 14, 28], (3, 1, 1)),
    ([1, 2, 3, 4, 5], (5, 0, 0)),
    ([13, 25, 30, 32, 33], (0, 1, 4)),
    ([5, 12, 13, 24, 25], (2, 2, 1)),
]


@pytest.mark.parametrize("front,expected", ZONE_CASES)
def test_zones(front, expected):
    assert StructureAnalyzer.zones(front) == expected


# ---------- 和值 ----------
SUM_CASES = [
    ([1, 2, 3, 4, 5], 15),
    ([10, 11, 18, 22, 35], 96),
    ([1, 8, 15, 22, 30], 76),
    ([13, 25, 30, 32, 33], 133),
    ([31, 32, 33, 34, 35], 165),
    ([1, 2, 3, 4, 35], 45),
]


@pytest.mark.parametrize("front,expected", SUM_CASES)
def test_front_sum(front, expected):
    assert StructureAnalyzer.front_sum(front) == expected


# ---------- 跨度 ----------
SPAN_CASES = [
    ([1, 2, 3, 4, 5], 4),
    ([10, 11, 18, 22, 35], 25),
    ([1, 8, 15, 22, 30], 29),
    ([13, 25, 30, 32, 33], 20),
    ([31, 32, 33, 34, 35], 4),
    ([1, 35, 3, 4, 5], 34),
]


@pytest.mark.parametrize("front,expected", SPAN_CASES)
def test_span(front, expected):
    assert StructureAnalyzer.span(front) == expected


# ---------- 连号 ----------
CONSEC_CASES = [
    ([1, 2, 3, 4, 5], 4),
    ([10, 11, 18, 22, 35], 1),
    ([1, 8, 15, 22, 30], 0),
    ([5, 6, 7, 20, 21], 3),
    ([13, 25, 30, 32, 33], 1),
    ([1, 3, 5, 7, 9], 0),
    ([2, 3, 4, 5, 6], 4),
    ([10, 12, 14, 16, 18], 0),
]


@pytest.mark.parametrize("front,expected", CONSEC_CASES)
def test_consecutive_pairs(front, expected):
    assert StructureAnalyzer.consecutive_pairs(front) == expected


# ---------- 单注指标对象 ----------
@pytest.mark.parametrize("i", range(20))
def test_metrics_basic(i):
    rng = random.Random(390 + i)
    front = sorted(rng.sample(range(1, 36), 5))
    m = StructureAnalyzer.analyze_single(front)
    assert isinstance(m, StructureMetrics)
    assert m.odd_count + m.even_count == 5
    assert m.big_count + m.small_count == 5
    assert m.zone1 + m.zone2 + m.zone3 == 5
    assert m.front_sum == sum(front)
    assert m.span == max(front) - min(front)
    assert 0 <= m.consecutive_pairs <= 4


# ---------- 评分 ----------
def test_balanced_high_score():
    r = analyze_combination([1, 8, 15, 22, 30], [6, 12])
    assert r.total_score >= 75
    assert "均衡" in r.assessment


def test_concentrated_low_score():
    r = analyze_combination([1, 2, 3, 4, 5], [6, 12])
    assert r.total_score < 60
    assert "偏集中" in r.assessment


@pytest.mark.parametrize("front", [
    [1, 2, 3, 4, 5],
    [1, 8, 15, 22, 30],
    [10, 11, 18, 22, 35],
    [13, 25, 30, 32, 33],
    [31, 32, 33, 34, 35],
    [1, 9, 17, 25, 33],
    [2, 8, 14, 20, 26],
    [5, 10, 15, 20, 25],
])
def test_score_range(front):
    r = analyze_combination(front)
    assert 0 <= r.total_score <= 100
    assert isinstance(r, CombinationScore)


@pytest.mark.parametrize("i", range(30))
def test_random_score_in_range(i):
    rng = random.Random(400 + i)
    front = sorted(rng.sample(range(1, 36), 5))
    r = analyze_combination(front)
    assert 0 <= r.total_score <= 100
    assert r.assessment in ("结构均衡", "结构略偏", "结构偏集中")


# ---------- 重复率 ----------
def test_duplicate_ratio_zero():
    tickets = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
               {"front": [8, 9, 10, 11, 12], "back": [13, 14]}]
    assert StructureAnalyzer.duplicate_ratio(tickets) == 0.0


def test_duplicate_ratio_high():
    tickets = [{"front": [10, 11, 18, 22, 35], "back": [6, 12]},
               {"front": [10, 11, 1, 2, 3], "back": [6, 7]},
               {"front": [10, 11, 5, 6, 7], "back": [6, 8]}]
    r = StructureAnalyzer.duplicate_ratio(tickets)
    assert r > 0.1


def test_duplicate_ratio_empty():
    assert StructureAnalyzer.duplicate_ratio([]) == 0.0


@pytest.mark.parametrize("n", range(10))
def test_duplicate_ratio_bounded(n):
    rng = random.Random(500 + n)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(5)]
    r = StructureAnalyzer.duplicate_ratio(tickets)
    assert 0.0 <= r <= 1.0


# ---------- 历史偏离度 ----------
@pytest.mark.parametrize("i", range(10))
def test_historical_deviation_bounded(i):
    rng = random.Random(600 + i)
    front = sorted(rng.sample(range(1, 36), 5))
    d = StructureAnalyzer.historical_deviation(front)
    assert 0.0 <= d <= 1.0


def test_historical_deviation_empty():
    d = StructureAnalyzer.historical_deviation([], "dlt")
    assert 0.0 <= d <= 1.0


# ---------- 多注组合分析 ----------
@pytest.mark.parametrize("n", [2, 3, 5, 8, 15])
def test_analyze_multi(n):
    rng = random.Random(700 + n)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(n)]
    r = StructureAnalyzer.analyze(tickets)
    assert 0 <= r.total_score <= 100
    assert "重复率" in r.assessment


def test_analyze_empty():
    r = StructureAnalyzer.analyze([])
    assert r.total_score == 0


def test_analyze_assessment_contains_disclaimer():
    tickets = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
               {"front": [8, 9, 10, 11, 12], "back": [8, 9]}]
    r = StructureAnalyzer.analyze(tickets)
    assert "随机性" in r.disclaimer


# ---------- to_dict / 结构 ----------
def test_score_to_dict():
    r = analyze_combination([1, 8, 15, 22, 30])
    d = r.to_dict()
    assert "score" in d
    assert "metrics" in d
    assert "assessment" in d
    assert "disclaimer" in d


def test_metrics_to_dict_fields():
    m = StructureAnalyzer.analyze_single([1, 8, 15, 22, 30])
    d = m.to_dict()
    for k in ("odd_even", "big_small", "zones", "front_sum", "span", "consecutive_pairs"):
        assert k in d


def test_disclaimer_not_prediction():
    r = analyze_combination([1, 2, 3, 4, 5])
    assert "中奖概率" in r.disclaimer or "随机性" in r.disclaimer
    assert "预测" not in r.disclaimer


# ---------- 边界 ----------
def test_score_single_empty():
    r = analyze_combination([])
    assert isinstance(r, CombinationScore)


def test_back_optional():
    m = StructureAnalyzer.analyze_single([1, 8, 15, 22, 30])
    assert m.back == []


def test_odd_even_ratio_format():
    m = StructureAnalyzer.analyze_single([1, 2, 3, 4, 5])
    assert m.odd_even_ratio == "3:2"


def test_zone_distribution_format():
    m = StructureAnalyzer.analyze_single([1, 13, 25, 30, 35])
    assert m.zone_distribution == "1-1-3"
