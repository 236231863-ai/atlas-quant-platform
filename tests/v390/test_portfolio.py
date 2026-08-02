"""v3.9.0 Phase 5：投注组合分析器测试。"""
from __future__ import annotations

import random

import pytest

from engine.lottery_quant.portfolio import (
    PortfolioAnalyzer,
    PortfolioReport,
    analyze_portfolio,
)

# ---------- 重复率 ----------
DUP_CASES = [
    ([{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
      {"front": [8, 9, 10, 11, 12], "back": [13, 14]}], 0.0),
    ([{"front": [10, 11, 18, 22, 35], "back": [6, 12]},
      {"front": [10, 11, 1, 2, 3], "back": [6, 7]},
      {"front": [10, 11, 5, 6, 7], "back": [6, 8]}], 4 / 13),
]


@pytest.mark.parametrize("tickets,expected", DUP_CASES)
def test_duplicate_ratio(tickets, expected):
    r = analyze_portfolio(tickets)
    assert r.duplicate_ratio == pytest.approx(expected, abs=0.01)


def test_duplicate_ratio_identical():
    t = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
         {"front": [1, 2, 3, 4, 5], "back": [6, 7]}]
    r = analyze_portfolio(t)
    assert r.duplicate_ratio > 0.5


# ---------- 相关性 ----------
def test_correlation_identical_notes():
    t = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
         {"front": [1, 2, 3, 4, 5], "back": [6, 7]}]
    assert PortfolioAnalyzer.correlation(t) == 1.0


def test_correlation_disjoint():
    t = [{"front": [1, 2, 3, 4, 5], "back": [6, 7]},
         {"front": [11, 12, 13, 14, 15], "back": [8, 9]}]
    assert PortfolioAnalyzer.correlation(t) == 0.0


def test_correlation_single_note():
    assert PortfolioAnalyzer.correlation([{"front": [1, 2, 3, 4, 5]}]) == 0.0


def test_correlation_empty():
    assert PortfolioAnalyzer.correlation([]) == 0.0


@pytest.mark.parametrize("overlap", range(1, 5))
def test_correlation_overlap(overlap):
    common = list(range(1, overlap + 1))
    t = [{"front": common + [10, 11, 12], "back": [6, 7]},
         {"front": common + [20, 21, 22], "back": [8, 9]}]
    corr = PortfolioAnalyzer.correlation(t)
    assert corr > 0
    assert corr < 1


# ---------- 覆盖范围 ----------
def test_coverage_all_same():
    t = [{"front": [1, 2, 3, 4, 5]}] * 5
    assert PortfolioAnalyzer.coverage(t) == pytest.approx(5 / 35, abs=0.01)


def test_coverage_wide():
    t = [{"front": [1, 7, 13, 19, 25]}, {"front": [2, 8, 14, 20, 26]},
         {"front": [3, 9, 15, 21, 27]}, {"front": [4, 10, 16, 22, 28]}]
    assert PortfolioAnalyzer.coverage(t) > 0.4


def test_coverage_ssq():
    t = [{"front": [1, 2, 3, 4, 5, 6]}, {"front": [7, 8, 9, 10, 11, 12]}]
    assert PortfolioAnalyzer.coverage(t, "ssq") == pytest.approx(12 / 33, abs=0.01)


@pytest.mark.parametrize("n", range(10))
def test_coverage_bounded(n):
    rng = random.Random(800 + n)
    t = [{"front": sorted(rng.sample(range(1, 36), 5))} for _ in range(5)]
    c = PortfolioAnalyzer.coverage(t)
    assert 0 < c <= 1


# ---------- 集中度 ----------
def test_concentration_identical():
    t = [{"front": [10, 11, 18, 22, 35]}] * 3
    # top3 号码占全部 15 个号码的 60%
    assert PortfolioAnalyzer.concentration(t) == pytest.approx(0.6, abs=0.01)


def test_concentration_low():
    t = [{"front": [1, 7, 13, 19, 25]}, {"front": [2, 8, 14, 20, 26]},
         {"front": [3, 9, 15, 21, 27]}]
    c = PortfolioAnalyzer.concentration(t)
    assert c < 0.5


@pytest.mark.parametrize("i", range(10))
def test_concentration_bounded(i):
    rng = random.Random(900 + i)
    t = [{"front": sorted(rng.sample(range(1, 36), 5))} for _ in range(5)]
    c = PortfolioAnalyzer.concentration(t)
    assert 0 <= c <= 1


# ---------- 风险评估 ----------
def test_high_risk():
    t = [{"front": [10, 11, 18, 22, 35]}, {"front": [10, 11, 18, 1, 2]},
         {"front": [10, 11, 18, 3, 4]}]
    r = analyze_portfolio(t)
    assert r.risk_assessment == "高"


def test_low_risk():
    t = [{"front": [1, 7, 13, 19, 25]}, {"front": [2, 8, 14, 20, 26]},
         {"front": [3, 9, 15, 21, 27]}]
    r = analyze_portfolio(t)
    assert r.risk_assessment == "低"


@pytest.mark.parametrize("i", range(20))
def test_risk_assessment_valid(i):
    rng = random.Random(1000 + i)
    t = [{"front": sorted(rng.sample(range(1, 36), 5)),
          "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(5)]
    r = analyze_portfolio(t)
    assert r.risk_assessment in ("低", "中", "高")


# ---------- 建议 ----------
def test_suggestions_non_empty():
    r = analyze_portfolio([{"front": [10, 11, 18, 22, 35], "back": [6, 12]}])
    assert len(r.suggestions) >= 1


def test_suggestions_high_dup():
    t = [{"front": [10, 11, 18, 22, 35]}, {"front": [10, 11, 18, 1, 2]},
         {"front": [10, 11, 18, 3, 4]}]
    r = analyze_portfolio(t)
    assert any("重复率" in s for s in r.suggestions)


def test_suggestions_balanced():
    t = [{"front": [1, 7, 13, 19, 25]}, {"front": [2, 8, 14, 20, 26]},
         {"front": [3, 9, 15, 21, 27]}]
    r = analyze_portfolio(t)
    assert any("均衡" in s or "保持" in s for s in r.suggestions)


@pytest.mark.parametrize("i", range(15))
def test_suggestions_structure_only(i):
    rng = random.Random(1100 + i)
    t = [{"front": sorted(rng.sample(range(1, 36), 5))} for _ in range(4)]
    r = analyze_portfolio(t)
    assert any("结构" in s or "理性" in s or "概率" in s for s in r.suggestions)


def test_suggestion_no_guarantee():
    t = [{"front": [1, 2, 3, 4, 5]}, {"front": [6, 7, 8, 9, 10]}]
    r = analyze_portfolio(t)
    assert any("不能保证" in s or "不改变" in s for s in r.suggestions)


# ---------- 报告结构 ----------
def test_report_type():
    r = analyze_portfolio([])
    assert isinstance(r, PortfolioReport)


def test_report_fields():
    r = analyze_portfolio([{"front": [1, 2, 3, 4, 5], "back": [6, 7]}])
    for f in ("note_count", "duplicate_ratio", "correlation", "coverage",
              "concentration", "risk_assessment", "suggestions", "disclaimer"):
        assert hasattr(r, f)


@pytest.mark.parametrize("f", ["duplicate_ratio", "correlation", "coverage",
                               "concentration", "risk_assessment", "suggestions"])
def test_report_dict_keys(f):
    r = analyze_portfolio([{"front": [1, 2, 3, 4, 5]}])
    assert f in r.to_dict()


def test_summary_text_fields():
    r = analyze_portfolio([{"front": [1, 2, 3, 4, 5], "back": [6, 7]}])
    t = r.summary_text()
    for kw in ("投注注数", "重复率", "相关性", "覆盖范围", "集中风险"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer():
    r = analyze_portfolio([])
    assert "不能保证中奖" in r.disclaimer
    assert "随机性" in r.disclaimer


def test_summary_has_disclaimer():
    r = analyze_portfolio([{"front": [1, 2, 3, 4, 5]}])
    assert "不能保证中奖" in r.summary_text()


# ---------- 边界 ----------
def test_empty_tickets():
    r = analyze_portfolio([])
    assert r.note_count == 0
    assert r.duplicate_ratio == 0


def test_single_ticket():
    r = analyze_portfolio([{"front": [1, 2, 3, 4, 5], "back": [6, 7]}])
    assert r.note_count == 1
    assert r.correlation == 0


def test_ssq_portfolio():
    t = [{"front": [1, 2, 3, 4, 5, 6], "back": [1]},
         {"front": [7, 8, 9, 10, 11, 12], "back": [2]}]
    r = analyze_portfolio(t, "ssq")
    assert r.lottery == "ssq"
    assert r.lottery_name == "双色球"


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_random_portfolio_matrix(seed):
    rng = random.Random(1200 + seed)
    t = [{"front": sorted(rng.sample(range(1, 36), 5)),
          "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(rng.randint(2, 10))]
    r = analyze_portfolio(t)
    assert 0 <= r.duplicate_ratio <= 1
    assert 0 <= r.correlation <= 1
    assert 0 < r.coverage <= 1
    assert 0 <= r.concentration <= 1
    assert r.risk_assessment in ("低", "中", "高")


@pytest.mark.parametrize("seed", range(30))
def test_ssq_portfolio_matrix(seed):
    rng = random.Random(1300 + seed)
    t = [{"front": sorted(rng.sample(range(1, 34), 6)),
          "back": [rng.randint(1, 16)]} for _ in range(rng.randint(3, 8))]
    r = analyze_portfolio(t, "ssq")
    assert r.lottery == "ssq"
    assert 0 <= r.duplicate_ratio <= 1
    assert 0 <= r.correlation <= 1
    assert 0 < r.coverage <= 1
    assert r.risk_assessment in ("低", "中", "高")


@pytest.mark.parametrize("seed", range(20))
def test_15_notes_portfolio(seed):
    """任务书场景：15 注组合分析。"""
    rng = random.Random(1400 + seed)
    t = [{"front": sorted(rng.sample(range(1, 36), 5)),
          "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(15)]
    r = analyze_portfolio(t)
    assert r.note_count == 15
    assert 0 <= r.duplicate_ratio <= 1
    assert len(r.suggestions) >= 1
    assert "不能保证中奖" in r.disclaimer
