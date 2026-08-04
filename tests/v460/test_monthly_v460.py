"""v4.6 P5：资产中心 2.0 月度复盘测试。

覆盖：月度聚合 / 净收益 / 诚实负期望 / 最近N月 / 文本报告。
"""
from __future__ import annotations

import pytest

from engine.asset_center import (
    MonthlyReport, MonthlyReportBuilder, MonthlySummary, build_monthly_report,
)


def mk(tid, buy_date, cost=2.0, win=False, lottery="dlt"):
    if win:
        return {"ticket_id": tid, "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": buy_date, "draw_date": "2026-08-01", "cost": cost}
    return {"ticket_id": tid, "lottery": lottery,
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": buy_date, "draw_date": "2026-08-01", "cost": cost}


# ---------- 月度聚合 ----------
def test_monthly_single_month():
    tickets = [mk("T-1", "2026-08-05"), mk("T-2", "2026-08-10")]
    rep = build_monthly_report(tickets)
    assert len(rep.items) == 1
    m = rep.items[0]
    assert m.year == 2026 and m.month == 8
    assert m.investment == 4.0
    assert m.ticket_count == 2


def test_monthly_multi_month():
    tickets = [mk("T-1", "2026-07-05"), mk("T-2", "2026-08-10")]
    rep = build_monthly_report(tickets)
    assert len(rep.items) == 2
    assert {m.month for m in rep.items} == {7, 8}


def test_monthly_win():
    tickets = [mk("T-1", "2026-08-05", win=True)]
    rep = build_monthly_report(tickets)
    m = rep.items[0]
    assert m.win_count == 1
    assert m.winnings >= 5_000_000
    assert m.net > 0


def test_monthly_net_negative():
    """诚实：不中奖则净收益为负。"""
    tickets = [mk("T-1", "2026-08-05"), mk("T-2", "2026-08-10")]
    rep = build_monthly_report(tickets)
    m = rep.items[0]
    assert m.net == -4.0
    assert m.investment == 4.0
    assert m.winnings == 0.0


def test_monthly_skip_bad_date():
    tickets = [{"ticket_id": "T-1", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
                "back": [1, 2], "buy_date": "", "draw_date": "", "cost": 2.0}]
    rep = build_monthly_report(tickets)
    assert rep.items == []


# ---------- 最近 N 月 ----------
def test_monthly_recent_months():
    tickets = [mk("T-1", f"2026-{m:02d}-05") for m in range(1, 7)]
    rep = build_monthly_report(tickets, months=3)
    assert len(rep.items) == 3
    assert rep.items[-1].month == 6


# ---------- 结构 ----------
def test_monthly_summary_props():
    m = MonthlySummary(year=2026, month=8, investment=120, winnings=7)
    assert m.net == -113
    assert m.label == "2026年8月"


def test_monthly_summary_to_dict():
    m = MonthlySummary(year=2026, month=8, investment=120, winnings=7)
    d = m.to_dict()
    assert d["net"] == -113
    assert d["year"] == 2026


def test_monthly_summary_text():
    m = MonthlySummary(year=2026, month=8, investment=120, winnings=7)
    assert "2026年8月" in m.text()
    assert "净收益" in m.text()


def test_report_total_net():
    rep = MonthlyReport(items=[MonthlySummary(year=2026, month=7, investment=50, winnings=10),
                               MonthlySummary(year=2026, month=8, investment=120, winnings=7)])
    assert rep.total_net == -153


def test_report_latest():
    rep = MonthlyReport(items=[MonthlySummary(year=2026, month=7, investment=50),
                               MonthlySummary(year=2026, month=8, investment=120)])
    assert rep.latest().month == 8


def test_report_to_dict():
    rep = build_monthly_report([mk("T-1", "2026-08-05")])
    d = rep.to_dict()
    assert len(d["items"]) == 1
    assert "total_net" in d


def test_report_text_disclaimer():
    rep = build_monthly_report([mk("T-1", "2026-08-05")])
    assert "负期望" in rep.to_text()
    assert "月度复盘" in rep.to_text()


def test_report_empty():
    rep = build_monthly_report([])
    assert rep.items == []
    assert rep.to_text()


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 5, 10])
def test_monthly_count_matrix(n):
    tickets = [mk(f"T-{i}", "2026-08-05") for i in range(n)]
    rep = build_monthly_report(tickets)
    if n == 0:
        assert rep.items == []
    else:
        assert rep.items[0].ticket_count == n


@pytest.mark.parametrize("m", range(1, 13))
def test_monthly_all_months(m):
    rep = build_monthly_report([mk("T-1", f"2026-{m:02d}-10")])
    assert rep.items[0].month == m


@pytest.mark.parametrize("i", range(10))
def test_monthly_random(i):
    import random
    random.seed(i)
    tickets = [mk(f"T-{j}", f"2026-{random.randint(1, 8):02d}-{random.randint(1, 28):02d}",
                  win=random.random() < 0.2) for j in range(random.randint(1, 10))]
    rep = build_monthly_report(tickets)
    assert len(rep.items) >= 1
    assert rep.to_text()
