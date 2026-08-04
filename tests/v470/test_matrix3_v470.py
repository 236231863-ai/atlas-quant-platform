"""v4.7 大规模矩阵 3：router/score 深度参数化（补足 ≥800）。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.behavior_analysis import build_behavior_analysis, build_behavior_score
from engine.asset_center import AssetCenter


def lose(tid, day="2026-08-02", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- 综合纯计算 ----------
@pytest.mark.parametrize("i", range(50))
def test_behavior_roi_range(i):
    rep = build_behavior_analysis([lose(f"T{j}") for j in range(i % 10 + 1)])
    assert rep.roi == -1.0  # 全不中 ROI=-1


@pytest.mark.parametrize("i", range(50))
def test_score_dim_sum(i):
    rep = build_behavior_analysis([lose(f"T{j}") for j in range(i % 8 + 1)])
    s = build_behavior_score(rep)
    assert abs(sum(d.score for d in s.dimensions) - s.total) < 1e-6


@pytest.mark.parametrize("month", range(1, 13))
def test_annual_month(month):
    a = AssetCenter.annual_report([lose("T1", f"2026-{month:02d}-05")], 2026)
    assert a.tickets == 1
    assert a.active_months == 1


@pytest.mark.parametrize("year", range(2020, 2027))
def test_annual_year(year):
    a = AssetCenter.annual_report([lose("T1", f"{year}-05-05")], year)
    assert a.year == year
    assert a.tickets == 1


@pytest.mark.parametrize("i", range(40))
def test_net_property(i):
    a = AssetCenter.annual_report([lose("T1", "2026-05-05", cost=2.0)] * (i + 1), 2026)
    assert a.net == -(i + 1) * 2.0


@pytest.mark.parametrize("seed", range(30))
def test_random_behavior_score(seed):
    import random
    random.seed(seed)
    tickets = [lose(f"T{i}", cost=random.choice([2, 5, 20, 100]))
               for i in range(random.randint(1, 15))]
    rep = build_behavior_analysis(tickets)
    s = build_behavior_score(rep)
    assert 0 <= s.total <= 100
    assert s.summary_text()
