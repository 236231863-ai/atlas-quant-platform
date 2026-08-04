"""v4.7 大规模矩阵 1：behavior/score 纯计算参数化。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.behavior_analysis import (
    BehaviorAnalyzer, build_behavior_analysis, build_behavior_score,
)


def win(tid, day="2026-08-01", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [10, 11, 18, 22, 35], "back": [6, 12],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


def lose(tid, day="2026-08-02", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- behavior 纯计算 ----------
@pytest.mark.parametrize("n", range(40))
def test_investment_scale(n):
    rep = build_behavior_analysis([lose(f"T{i}") for i in range(n)])
    assert rep.total_investment == n * 2.0


@pytest.mark.parametrize("n", range(30))
def test_win_scale(n):
    rep = build_behavior_analysis([win(f"T{i}") for i in range(n)])
    assert rep.win_count == n
    assert rep.total_winnings >= n * 5_000_000


@pytest.mark.parametrize("n", range(20))
def test_loss_streak_scale(n):
    rep = build_behavior_analysis([lose(f"T{i}") for i in range(n)])
    assert rep.current_loss_streak == n
    assert rep.max_loss_streak == n


@pytest.mark.parametrize("i", range(30))
def test_net_calc(i):
    rep = build_behavior_analysis([lose(f"T{i % 3}", cost=2.0) for i in range(i)])
    assert rep.net == -rep.total_investment


@pytest.mark.parametrize("cost", [0.5, 1, 2, 5, 10, 20, 50, 100])
def test_avg_cost(cost):
    rep = build_behavior_analysis([lose("T1", cost=cost)])
    assert rep.avg_per_bet == cost


# ---------- score 纯计算 ----------
@pytest.mark.parametrize("n", range(1, 31))
def test_score_total_range(n):
    rep = build_behavior_analysis([lose(f"T{i}") for i in range(n)])
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


@pytest.mark.parametrize("freq", range(0, 31))
def test_score_frequency(freq):
    rep = build_behavior_analysis([lose("T1")])
    rep.bet_frequency = freq
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100


@pytest.mark.parametrize("cost", [2, 5, 20, 50, 100, 200, 500])
def test_score_cost(cost):
    rep = build_behavior_analysis([lose("T1", cost=cost)])
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100
    assert s.level in ("优秀", "良好", "需关注", "高风险")


@pytest.mark.parametrize("i", range(30))
def test_score_stable(i):
    rep = build_behavior_analysis([lose(f"T{i}") for i in range(i % 10 + 1)])
    s = build_behavior_score(rep)
    assert len(s.dimensions) == 4
    assert sum(d.max_score for d in s.dimensions) == 100
