"""v3.9.0 Phase 1：概率计算引擎测试。"""
from __future__ import annotations

import math

import pytest

from engine.lottery_quant.probability import (
    ProbabilityModel,
    ProbabilityReport,
    PrizeProbability,
    dlt_probabilities,
    ssq_probabilities,
)

# ---------- 总组合数 ----------
def test_dlt_total_combinations():
    assert ProbabilityModel.dlt_total() == 21_425_712


def test_ssq_total_combinations():
    assert ProbabilityModel.ssq_total() == 17_721_088


def test_dlt_total_formula():
    assert ProbabilityModel.dlt_total() == math.comb(35, 5) * math.comb(12, 2)


def test_ssq_total_formula():
    assert ProbabilityModel.ssq_total() == math.comb(33, 6) * 16


# ---------- 一等奖概率 ----------
def test_dlt_first_prize_one_in():
    assert dlt_probabilities().first_prize_one_in == 21_425_712


def test_ssq_first_prize_one_in():
    assert ssq_probabilities().first_prize_one_in == 17_721_088


def test_dlt_first_prize_ways_is_one():
    assert ProbabilityModel.dlt_ways(5, 2) == 1


def test_ssq_first_prize_ways_is_one():
    assert ProbabilityModel.ssq_ways(6, 1) == 1


# ---------- 大乐透各奖级组合数 ----------
DLT_WAYS_EXPECT = {
    (5, 2): 1,
    (5, 1): 20,
    (5, 0): 45,
    (4, 2): 150,
    (4, 1): 3000,
    (3, 2): 4350,
    (4, 0): 6750,
    (3, 1): 87000,
    (2, 2): 40600,
    (3, 0): 195750,
    (1, 2): 137025,
    (2, 1): 812000,
    (0, 2): 142506,
}


@pytest.mark.parametrize("fh,bh", [(5, 2), (5, 1), (5, 0), (4, 2), (4, 1),
                                   (3, 2), (4, 0), (3, 1), (2, 2), (3, 0),
                                   (1, 2), (2, 1), (0, 2)])
def test_dlt_ways_exact(fh, bh):
    assert ProbabilityModel.dlt_ways(fh, bh) == DLT_WAYS_EXPECT[(fh, bh)]


# ---------- 双色球各奖级组合数 ----------
SSQ_WAYS_EXPECT = {
    (6, 1): 1,
    (6, 0): 15,
    (5, 1): 162,
    (5, 0): 2430,
    (4, 1): 5265,
    (4, 0): 78975,
    (3, 1): 58500,
    (2, 1): 263250,
    (1, 1): 484380,
    (0, 1): 296010,
}


@pytest.mark.parametrize("rh,bh", [(6, 1), (6, 0), (5, 1), (5, 0), (4, 1),
                                   (4, 0), (3, 1), (2, 1), (1, 1), (0, 1)])
def test_ssq_ways_exact(rh, bh):
    assert ProbabilityModel.ssq_ways(rh, bh) == SSQ_WAYS_EXPECT[(rh, bh)]


# ---------- 命中矩阵（所有可能命中数）----------
_ALL_DLT = [(fh, bh) for fh in range(6) for bh in range(3)]
_ALL_SSQ = [(rh, bh) for rh in range(7) for bh in range(2)]


@pytest.mark.parametrize("fh,bh", _ALL_DLT)
def test_dlt_ways_non_negative(fh, bh):
    ways = ProbabilityModel.dlt_ways(fh, bh)
    assert ways >= 0
    assert ways <= ProbabilityModel.dlt_total()


@pytest.mark.parametrize("fh,bh", _ALL_DLT)
def test_dlt_probability_in_range(fh, bh):
    ways = ProbabilityModel.dlt_ways(fh, bh)
    p = ways / ProbabilityModel.dlt_total()
    assert 0 <= p <= 1


@pytest.mark.parametrize("rh,bh", _ALL_SSQ)
def test_ssq_ways_non_negative(rh, bh):
    ways = ProbabilityModel.ssq_ways(rh, bh)
    assert ways >= 0
    assert ways <= ProbabilityModel.ssq_total()


@pytest.mark.parametrize("rh,bh", _ALL_SSQ)
def test_ssq_probability_in_range(rh, bh):
    ways = ProbabilityModel.ssq_ways(rh, bh)
    p = ways / ProbabilityModel.ssq_total()
    assert 0 <= p <= 1


# ---------- 概率报告结构 ----------
def test_dlt_report_type():
    r = dlt_probabilities()
    assert isinstance(r, ProbabilityReport)
    assert r.lottery == "dlt"
    assert r.lottery_name == "大乐透"


def test_dlt_report_prize_count():
    r = dlt_probabilities()
    assert len(r.prizes) == 13


def test_ssq_report_prize_count():
    r = ssq_probabilities()
    assert len(r.prizes) == 10


def test_prize_probability_fields():
    r = dlt_probabilities()
    p = r.prizes[0]
    assert isinstance(p, PrizeProbability)
    assert p.level == "一等奖"
    assert p.hit_desc == "5+2"
    assert p.ways == 1
    assert p.one_in == 21_425_712


@pytest.mark.parametrize("i", range(13))
def test_dlt_prize_probability_sane(i):
    r = dlt_probabilities()
    p = r.prizes[i]
    assert p.probability == p.ways / r.total_combinations
    assert p.one_in == r.total_combinations / p.ways


# ---------- 总中奖率 ----------
def test_dlt_total_win_probability():
    r = dlt_probabilities()
    assert 0.06 < r.total_win_probability < 0.07


def test_ssq_total_win_probability():
    r = ssq_probabilities()
    assert 0.06 < r.total_win_probability < 0.07


def test_dlt_sum_of_ways_matches():
    """所有可能命中组合数之和 = 总组合数。"""
    total_ways = sum(ProbabilityModel.dlt_ways(fh, bh) for fh in range(6) for bh in range(3))
    assert total_ways == ProbabilityModel.dlt_total()


def test_ssq_sum_of_ways_matches():
    total_ways = sum(ProbabilityModel.ssq_ways(rh, bh) for rh in range(7) for bh in range(2))
    assert total_ways == ProbabilityModel.ssq_total()


# ---------- 免责声明 ----------
def test_dlt_report_has_disclaimer():
    r = dlt_probabilities()
    assert "随机性" in r.disclaimer


def test_ssq_report_has_disclaimer():
    r = ssq_probabilities()
    assert "随机性" in r.disclaimer


def test_summary_text_contains_disclaimer():
    r = dlt_probabilities()
    assert "随机性" in r.summary_text()


def test_summary_text_contains_first_prize():
    r = dlt_probabilities()
    assert "21,425,712" in r.summary_text()


# ---------- to_dict ----------
def test_report_to_dict():
    r = dlt_probabilities()
    d = r.to_dict()
    assert d["lottery"] == "dlt"
    assert d["first_prize_one_in"] == 21_425_712
    assert len(d["prizes"]) == 13


def test_prize_to_dict():
    r = dlt_probabilities()
    d = r.prizes[0].to_dict()
    assert d["level"] == "一等奖"
    assert d["ways"] == 1


# ---------- 精确分数验证 ----------
def test_dlt_second_prize_probability():
    """二等奖 (5,1) = 20/21,425,712。"""
    assert ProbabilityModel.dlt_ways(5, 1) == 20


def test_dlt_win_probability_exact():
    win = sum(ProbabilityModel.dlt_ways(fh, bh) for (fh, bh), _ in [
        ((5, 2), "一等奖"), ((5, 1), "二等奖"), ((5, 0), "三等奖"),
        ((4, 2), "四等奖"), ((4, 1), "五等奖"), ((3, 2), "六等奖"),
        ((4, 0), "七等奖"), ((3, 1), "八等奖"), ((2, 2), "八等奖"),
        ((3, 0), "九等奖"), ((1, 2), "九等奖"), ((2, 1), "九等奖"), ((0, 2), "九等奖"),
    ])
    assert win == 1_429_197


def test_ssq_win_probability_exact():
    win = sum(ProbabilityModel.ssq_ways(rh, bh) for (rh, bh), _ in [
        ((6, 1), "一等奖"), ((6, 0), "二等奖"), ((5, 1), "三等奖"),
        ((5, 0), "四等奖"), ((4, 1), "四等奖"), ((4, 0), "五等奖"),
        ((3, 1), "五等奖"), ((2, 1), "六等奖"), ((1, 1), "六等奖"), ((0, 1), "六等奖"),
    ])
    assert win == 1_188_988
