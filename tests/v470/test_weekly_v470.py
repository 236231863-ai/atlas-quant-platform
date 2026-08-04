"""v4.7 P6：每周彩票报告测试。

覆盖：本周聚合 / 偏移周 / 风险提醒 / 留存价值。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.behavior_analysis import (
    WeeklyReport, WeeklyReportBuilder, build_weekly_report,
)

TODAY = date.today()
MONDAY = TODAY - timedelta(days=TODAY.weekday())


def t(tid, day, cost=2.0, win=False):
    if win:
        return {"ticket_id": tid, "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": day, "draw_date": "2026-08-01", "cost": cost}
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- 本周报告 ----------
def test_empty_week():
    rep = build_weekly_report([])
    assert rep.ticket_count == 0
    assert "暂无购彩记录" in rep.risk_note


def test_this_week():
    rep = build_weekly_report([t("T1", MONDAY.isoformat())])
    assert rep.ticket_count == 1
    assert rep.investment == 2.0


def test_this_week_includes_sunday():
    sunday = (MONDAY + timedelta(days=6)).isoformat()
    rep = build_weekly_report([t("T1", sunday)])
    assert rep.ticket_count == 1


def test_week_excludes_other_week():
    last_sunday = (MONDAY - timedelta(days=1)).isoformat()
    rep = build_weekly_report([t("T1", last_sunday)])
    assert rep.ticket_count == 0


def test_win_in_week():
    rep = build_weekly_report([t("T1", MONDAY.isoformat(), win=True)])
    assert rep.win_count == 1
    assert rep.winnings >= 5_000_000


def test_net():
    rep = build_weekly_report([t("T1", MONDAY.isoformat()), t("T2", MONDAY.isoformat())])
    assert rep.net == -4.0


# ---------- 偏移周 ----------
def test_offset_week():
    last_week = build_weekly_report([t("T1", (MONDAY - timedelta(days=3)).isoformat())],
                                    offset=-1)
    assert last_week.ticket_count == 1


def test_offset_zero_default():
    rep = build_weekly_report([t("T1", MONDAY.isoformat())], offset=0)
    assert rep.ticket_count == 1


# ---------- 风险提醒 ----------
def test_risk_high_frequency():
    tickets = [t(f"T{i}", MONDAY.isoformat()) for i in range(12)]
    rep = build_weekly_report(tickets)
    assert "频繁" in rep.risk_note


def test_risk_high_investment():
    rep = build_weekly_report([t("T1", MONDAY.isoformat(), cost=200)])
    assert "投入偏高" in rep.risk_note


def test_risk_no_win():
    tickets = [t(f"T{i}", MONDAY.isoformat()) for i in range(3)]
    rep = build_weekly_report(tickets)
    assert "未中奖" in rep.risk_note


def test_risk_none_when_ok():
    rep = build_weekly_report([t("T1", MONDAY.isoformat())])
    assert rep.risk_note == ""


# ---------- 结构 ----------
def test_summary_text():
    rep = build_weekly_report([t("T1", MONDAY.isoformat())])
    assert "本周彩票报告" in rep.summary_text()
    assert "随机性" in rep.summary_text()


def test_to_dict():
    rep = build_weekly_report([t("T1", MONDAY.isoformat())])
    d = rep.to_dict()
    assert "net" in d and "risk_note" in d


def test_week_bounds():
    start, end = WeeklyReportBuilder._week_bounds(TODAY)
    assert start == MONDAY.isoformat()
    assert end == (MONDAY + timedelta(days=6)).isoformat()


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 5, 10, 15])
def test_week_scale(n):
    tickets = [t(f"T{i}", MONDAY.isoformat()) for i in range(n)]
    rep = build_weekly_report(tickets)
    assert rep.ticket_count == n
    assert rep.investment == n * 2.0


@pytest.mark.parametrize("offset", range(-3, 4))
def test_week_offset(offset):
    rep = build_weekly_report([t("T1", (MONDAY + timedelta(weeks=offset)).isoformat())],
                              offset=offset)
    assert rep.ticket_count == 1


@pytest.mark.parametrize("seed", range(10))
def test_week_random(seed):
    import random
    random.seed(seed)
    tickets = [t(f"T{i}", (MONDAY + timedelta(days=random.randint(0, 6))).isoformat(),
                 win=random.random() < 0.2) for i in range(random.randint(1, 12))]
    rep = build_weekly_report(tickets)
    assert rep.ticket_count == len(tickets)
    assert rep.summary_text()
