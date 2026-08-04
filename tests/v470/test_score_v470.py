"""v4.7 P2：投注健康评分测试。

覆盖：四维度 / 总分 / 等级 / 优势/风险 / 非中奖评分 / 边界。
"""
from __future__ import annotations

import pytest

from engine.behavior_analysis import (
    BehaviorScore, BehaviorScoreBuilder, ScoreDimension, build_behavior_score,
)
from engine.behavior_analysis.analysis import BehaviorAnalyzer


def make_rep(n=3, cost=2.0, frequency=3.0, win=False, loss_streak=0):
    """构造 UserBehaviorReport。"""
    tickets = []
    for i in range(n):
        if win and i == n - 1:
            t = {"ticket_id": f"W{i}", "lottery": "dlt",
                 "front": [10, 11, 18, 22, 35], "back": [6, 12],
                 "buy_date": f"2026-08-{i + 1:02d}", "draw_date": "2026-08-01", "cost": cost}
        else:
            t = {"ticket_id": f"L{i}", "lottery": "dlt",
                 "front": [1, 2, 3, 4, 5], "back": [1, 2],
                 "buy_date": f"2026-08-{i + 1:02d}", "draw_date": "2026-08-01", "cost": cost}
        tickets.append(t)
    rep = BehaviorAnalyzer.build(tickets)
    rep.bet_frequency = frequency
    rep.max_loss_streak = loss_streak if loss_streak else rep.max_loss_streak
    return rep


# ---------- 总分 ----------
def test_score_range():
    rep = make_rep()
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


def test_score_non_negative():
    rep = make_rep(n=1, cost=100)
    s = build_behavior_score(rep)
    assert s.total >= 0


def test_score_empty():
    rep = BehaviorAnalyzer.build([])
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


# ---------- 维度 ----------
def test_dimensions_count():
    rep = make_rep()
    s = build_behavior_score(rep)
    assert len(s.dimensions) == 4


def test_dimension_names():
    rep = make_rep()
    s = build_behavior_score(rep)
    names = [d.name for d in s.dimensions]
    assert names == ["资金管理", "投注纪律", "复盘习惯", "风险意识"]


def test_dimension_max():
    rep = make_rep()
    s = build_behavior_score(rep)
    assert [d.max_score for d in s.dimensions] == [40, 30, 20, 10]


def test_dimension_ratio():
    d = ScoreDimension("测试", 20, 40)
    assert d.ratio == 0.5


# ---------- 等级 ----------
def test_level_excellent():
    s = BehaviorScore(total=85)
    assert s.level == "优秀"


def test_level_good():
    s = BehaviorScore(total=65)
    assert s.level == "良好"


def test_level_watch():
    s = BehaviorScore(total=50)
    assert s.level == "需关注"


def test_level_high_risk():
    s = BehaviorScore(total=30)
    assert s.level == "高风险"


# ---------- 优势/风险 ----------
def test_strengths():
    rep = make_rep(n=3, cost=2, frequency=3)
    s = build_behavior_score(rep)
    assert s.strengths  # 有优势


def test_risks_high_freq():
    rep = make_rep(frequency=30)
    s = build_behavior_score(rep)
    assert any("频率过高" in r for r in s.risks)


def test_risks_high_cost():
    rep = make_rep(cost=100)
    s = build_behavior_score(rep)
    assert any("投入偏高" in r for r in s.risks)


def test_risks_loss():
    rep = make_rep(n=5, loss_streak=20)
    s = build_behavior_score(rep)
    assert any("亏损" in r for r in s.risks) or any("未中" in r for r in s.risks)


# ---------- 非中奖评分 ----------
def test_no_win_promotion():
    """不输出「中奖概率提升」。"""
    rep = make_rep(win=True)
    s = build_behavior_score(rep)
    text = s.summary_text()
    assert "中奖概率提升" not in text


def test_summary_has_dimensions():
    rep = make_rep()
    s = build_behavior_score(rep)
    assert "购彩健康分" in s.summary_text()


def test_disclaimer():
    assert "随机性" in BehaviorScore().disclaimer


# ---------- 结构 ----------
def test_to_dict():
    rep = make_rep()
    s = build_behavior_score(rep)
    d = s.to_dict()
    assert "total" in d and "level" in d and "dimensions" in d


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 3, 10])
def test_score_ticket_scale(n):
    rep = make_rep(n=n)
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


@pytest.mark.parametrize("cost", [1, 2, 10, 50, 100, 200])
def test_score_cost_scale(cost):
    rep = make_rep(cost=cost)
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


@pytest.mark.parametrize("seed", range(15))
def test_score_random(seed):
    import random
    random.seed(seed)
    rep = make_rep(n=random.randint(1, 10), cost=random.choice([2, 5, 20, 100]),
                   frequency=random.randint(1, 30))
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100
    assert s.summary_text()
