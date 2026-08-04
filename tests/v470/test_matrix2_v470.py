"""v4.7 大规模矩阵 2：annual/strategy/weekly 参数化。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.asset_center import AnnualSummary, AssetCenter
from engine.strategy_review import build_strategy_review
from engine.behavior_analysis import build_weekly_report

MONDAY = date.today() - timedelta(days=date.today().weekday())


def t(tid, day="2026-08-01", cost=2.0, win=False):
    if win:
        return {"ticket_id": tid, "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": day, "draw_date": "2026-08-01", "cost": cost,
                "prize_level": "一等奖"}
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- annual 矩阵 ----------
@pytest.mark.parametrize("i", range(40))
def test_annual_roi_calc(i):
    a = AnnualSummary(year=2026, investment=i * 10, winnings=i * 2)
    expected = (i * 2 - i * 10) / (i * 10) if i else 0.0
    assert abs(a.roi - expected) < 1e-6


@pytest.mark.parametrize("n", range(1, 21))
def test_annual_invest(n):
    tickets = [t(f"T{i}", f"2026-{i % 12 + 1:02d}-05") for i in range(n)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.investment == n * 2.0


@pytest.mark.parametrize("n", range(1, 16))
def test_annual_drawdown_no_win(n):
    tickets = [t(f"T{i}", f"2026-{i % 12 + 1:02d}-05") for i in range(n)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.max_drawdown == n * 2.0


# ---------- strategy 矩阵 ----------
@pytest.mark.parametrize("n", range(1, 21))
def test_strategy_unique(n):
    tickets = [t(f"T{i}", front=[1 + i, 2 + i, 3 + i, 4 + i, 5 + i], back=[1, 2])
               if False else {"ticket_id": f"T{i}", "lottery": "dlt",
                              "front": [1 + i, 2 + i, 3 + i, 4 + i, 5 + i],
                              "back": [1, 2], "buy_date": "2026-08-01",
                              "draw_date": "2026-08-01", "cost": 2.0}
               for i in range(n)]
    r = build_strategy_review(tickets)
    assert r.unique_combos == n
    assert r.random_count == n


@pytest.mark.parametrize("dup", range(1, 11))
def test_strategy_doubled(dup):
    tickets = [{"ticket_id": f"T{i}", "lottery": "dlt",
                "front": [1, 2, 3, 4, 5], "back": [1, 2],
                "buy_date": "2026-08-01", "draw_date": "2026-08-01", "cost": 2.0}
               for i in range(dup)]
    r = build_strategy_review(tickets)
    if dup == 1:
        assert r.fixed_combo_count == 0
    else:
        assert r.fixed_combo_count == 1
        assert r.doubled_times == dup - 1


# ---------- weekly 矩阵 ----------
@pytest.mark.parametrize("n", range(0, 21))
def test_weekly_count(n):
    tickets = [{"ticket_id": f"T{i}", "lottery": "dlt",
                "front": [1, 2, 3, 4, 5], "back": [1, 2],
                "buy_date": (MONDAY + timedelta(days=i % 7)).isoformat(),
                "draw_date": "2026-08-01", "cost": 2.0} for i in range(n)]
    rep = build_weekly_report(tickets)
    assert rep.ticket_count == n


@pytest.mark.parametrize("offset", range(-5, 6))
def test_weekly_offset_range(offset):
    day = (MONDAY + timedelta(weeks=offset, days=3)).isoformat()
    rep = build_weekly_report([t("T1", day)], offset=offset)
    assert rep.ticket_count == 1


@pytest.mark.parametrize("i", range(30))
def test_weekly_risk_variants(i):
    n = (i % 15) + 1
    tickets = [{"ticket_id": f"T{j}", "lottery": "dlt",
                "front": [1, 2, 3, 4, 5], "back": [1, 2],
                "buy_date": MONDAY.isoformat(), "draw_date": "2026-08-01",
                "cost": 2.0 if j % 3 else 100.0} for j in range(n)]
    rep = build_weekly_report(tickets)
    assert rep.summary_text()
