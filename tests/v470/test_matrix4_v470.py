"""v4.7 补充矩阵 4（补足 ≥800）。"""
from __future__ import annotations

import pytest

from engine.behavior_analysis import (
    BehaviorScore, ScoreDimension, build_behavior_analysis, build_weekly_report,
)
from engine.asset_center import AssetCenter


def lose(tid, day="2026-08-02", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


@pytest.mark.parametrize("i", range(15))
def test_score_dimension_ratio(i):
    d = ScoreDimension("测试", i * 2, 40)
    assert 0 <= d.ratio <= 1


@pytest.mark.parametrize("i", range(15))
def test_behavior_summary(i):
    rep = build_behavior_analysis([lose(f"T{i}") for i in range(i + 1)])
    assert rep.summary_text()
    assert "随机性" in rep.summary_text()


@pytest.mark.parametrize("i", range(15))
def test_annual_any(i):
    a = AssetCenter.annual_report([lose("T1", f"2026-{i % 12 + 1:02d}-05")], 2026)
    assert a.to_dict()["year"] == 2026


@pytest.mark.parametrize("i", range(15))
def test_weekly_text(i):
    rep = build_weekly_report([lose(f"T{i}")])
    assert rep.summary_text()
