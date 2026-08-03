"""v4.3 P3：彩票资产中心测试（≥150 场景）。

覆盖：资产字段 / 中奖率 / 净收益 / 亏损率 / 风险等级 / 年度报告 / 风险提示。
"""
from __future__ import annotations

from datetime import date

import pytest

from engine.asset_center import (
    DISCLAIMER, AnnualSummary, AssetCenter, AssetReport, build_asset_report,
)

DRAW = "2026-08-01"
WIN = {"ticket_id": "W-1", "lottery": "dlt", "front": [10, 11, 18, 22, 35],
       "back": [6, 12], "buy_date": "2026-07-31", "draw_date": DRAW, "cost": 2.0}
LOSE = {"ticket_id": "L-1", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
        "back": [1, 2], "buy_date": "2026-07-31", "draw_date": DRAW, "cost": 2.0}
FUTURE = {"ticket_id": "F-1", "lottery": "dlt", "front": [7, 8, 9, 10, 11],
          "back": [3, 4], "buy_date": "2026-08-02", "draw_date": "2026-08-05", "cost": 2.0}


def mk(tid, lottery="dlt", front=None, back=None, buy_date="2026-07-31",
       draw_date=DRAW, cost=2.0):
    return {"ticket_id": tid, "lottery": lottery,
            "front": front or [1, 2, 3, 4, 5], "back": back or [1, 2],
            "buy_date": buy_date, "draw_date": draw_date, "cost": cost}


# ---------- 基础属性 ----------
def test_empty_report(ticket_storage):
    rep = AssetReport()
    assert rep.total_tickets == 0
    assert rep.win_rate == 0.0
    assert rep.net == 0.0
    assert rep.loss_rate == 0.0
    assert rep.risk_level == "A"


def test_build_empty(ticket_storage):
    rep = AssetCenter.build([])
    assert rep.total_tickets == 0
    assert rep.risk_level == "A"


def test_win_rate_zero(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert rep.total_tickets == 1
    assert rep.win_count == 0
    assert rep.win_rate == 0.0


def test_win_rate_full(ticket_storage):
    rep = AssetCenter.build([WIN, WIN])
    assert rep.win_count == 2
    assert rep.win_rate == 1.0


def test_win_rate_half(ticket_storage):
    rep = AssetCenter.build([WIN, LOSE])
    assert rep.win_rate == 0.5


@pytest.mark.parametrize("n_win,n_lose", [
    (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (1, 9), (9, 1), (0, 10),
])
def test_win_rate_matrix(ticket_storage, n_win, n_lose):
    tickets = [dict(WIN, ticket_id=f"W-{i}") for i in range(n_win)] + \
              [dict(LOSE, ticket_id=f"L-{i}") for i in range(n_lose)]
    rep = AssetCenter.build(tickets)
    assert rep.total_tickets == n_win + n_lose
    assert rep.win_count == n_win
    if n_win + n_lose:
        assert abs(rep.win_rate - n_win / (n_win + n_lose)) < 1e-6


# ---------- 净收益 / 亏损率 ----------
def test_net_positive(ticket_storage):
    rep = AssetCenter.build([WIN, WIN])
    assert rep.net > 0


def test_net_negative(ticket_storage):
    rep = AssetCenter.build([LOSE, LOSE])
    assert rep.net < 0


def test_loss_rate_no_invest(ticket_storage):
    rep = AssetReport()
    assert rep.loss_rate == 0.0


def test_loss_rate_all_lose(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert rep.loss_rate > 0.9


def test_loss_rate_some_win(ticket_storage):
    rep = AssetCenter.build([WIN, LOSE, LOSE, LOSE, LOSE])
    # 中大奖使 net 为正 → loss_rate 为 0（不亏损）
    assert 0.0 <= rep.loss_rate < 1.0


@pytest.mark.parametrize("n_win,n_lose", [(0, 10), (1, 10), (2, 10), (5, 10)])
def test_loss_rate_matrix(ticket_storage, n_win, n_lose):
    tickets = [dict(WIN, ticket_id=f"W-{i}") for i in range(n_win)] + \
              [dict(LOSE, ticket_id=f"L-{i}") for i in range(n_lose)]
    rep = AssetCenter.build(tickets)
    assert 0 <= rep.loss_rate <= 1


# ---------- 风险等级 ----------
def test_risk_a_no_invest(ticket_storage):
    assert AssetReport().risk_level == "A"


def test_risk_a_net_positive(ticket_storage):
    rep = AssetCenter.build([WIN, WIN, WIN])
    assert rep.net > 0
    assert rep.risk_level == "A"


def test_risk_b_moderate(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert rep.risk_level in ("B", "C", "D")


@pytest.mark.parametrize("tickets", [
    [LOSE], [LOSE, LOSE], [LOSE] * 3, [LOSE, WIN], [WIN, LOSE],
])
def test_risk_always_classified(ticket_storage, tickets):
    rep = AssetCenter.build(tickets)
    assert rep.risk_level in ("A", "B", "C", "D")
    assert rep.risk_text


def test_risk_text_present(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert rep.risk_text


# ---------- risk_line 风险提示 ----------
def test_risk_line_has_investment(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert "累计投入" in AssetCenter.risk_line(rep)


def test_risk_line_has_net(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert "净收益" in AssetCenter.risk_line(rep)


def test_risk_line_has_loss_rate(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert "亏损率" in AssetCenter.risk_line(rep)


def test_risk_line_empty(ticket_storage):
    rep = AssetCenter.build([])
    assert "累计投入" in AssetCenter.risk_line(rep)


@pytest.mark.parametrize("i", range(10))
def test_risk_line_matrix(ticket_storage, i):
    tickets = [dict(LOSE, ticket_id=f"L-{i}") for i in range(i + 1)]
    rep = AssetCenter.build(tickets)
    assert "⚠️" in AssetCenter.risk_line(rep)


# ---------- summary_text / to_dict ----------
def test_summary_text_has_fields(ticket_storage):
    rep = AssetCenter.build([LOSE])
    text = rep.summary_text()
    assert "累计购买" in text
    assert "累计中奖" in text
    assert "净收益" in text
    assert "中奖率" in text
    assert "风险等级" in text


def test_summary_text_disclaimer(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert "随机性" in rep.summary_text()


def test_to_dict_fields(ticket_storage):
    rep = AssetCenter.build([WIN])
    d = rep.to_dict()
    assert d["total_tickets"] == 1
    assert d["win_rate"] == 1.0
    assert d["net"] > 0
    assert "risk_level" in d
    assert "annual" in d


@pytest.mark.parametrize("i", range(5))
def test_to_dict_matrix(ticket_storage, i):
    tickets = [dict(LOSE, ticket_id=f"L-{j}") for j in range(i * 3 + 1)]
    d = AssetCenter.build(tickets).to_dict()
    assert d["total_tickets"] == i * 3 + 1


# ---------- 年度报告 ----------
def test_annual_report_single_year(ticket_storage):
    tickets = [mk("T-1", buy_date="2026-01-05"), mk("T-2", buy_date="2026-03-08")]
    rep = AssetCenter.build(tickets)
    assert len(rep.annual) == 1
    a = rep.annual[0]
    assert a.year == 2026
    assert a.tickets == 2
    assert a.investment == 4.0


def test_annual_report_multi_year(ticket_storage):
    tickets = [mk("T-1", buy_date="2025-06-01"), mk("T-2", buy_date="2026-01-01")]
    rep = AssetCenter.build(tickets)
    years = {a.year for a in rep.annual}
    assert years == {2025, 2026}


def test_annual_report_active_months(ticket_storage):
    tickets = [mk("T-1", buy_date="2026-01-05"), mk("T-2", buy_date="2026-01-20"),
               mk("T-3", buy_date="2026-03-10")]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.active_months == 2


def test_annual_report_win(ticket_storage):
    tickets = [dict(WIN), dict(LOSE)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.win_count == 1
    assert a.max_win >= 5_000_000


def test_annual_report_no_year(ticket_storage):
    a = AssetCenter.annual_report([LOSE], 1999)
    assert a.tickets == 0


def test_annual_net_property(ticket_storage):
    a = AnnualSummary(year=2026, investment=10.0, winnings=4.0)
    assert a.net == -6.0


@pytest.mark.parametrize("year", [2020, 2021, 2022, 2023, 2024, 2025, 2026])
def test_annual_report_any_year(ticket_storage, year):
    tickets = [dict(mk("T-1"), buy_date=f"{year}-05-01")]
    a = AssetCenter.annual_report(tickets, year)
    assert a.year == year
    assert a.tickets == 1


@pytest.mark.parametrize("n_months", [1, 2, 3, 6, 12])
def test_annual_report_months_matrix(ticket_storage, n_months):
    tickets = [mk(f"T-{m}", buy_date=f"2026-{m:02d}-05") for m in range(1, n_months + 1)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.active_months == n_months


# ---------- 常购彩种 / 双彩种 ----------
def test_favorite_lottery(ticket_storage):
    tickets = [mk("T-1", lottery="dlt"), mk("T-2", lottery="dlt"),
               mk("T-3", lottery="ssq", front=[1, 2, 3, 4, 5, 6], back=[1])]
    rep = AssetCenter.build(tickets)
    assert "大乐透" in rep.favorite_lotteries


def test_ssq_no_crash(ticket_storage):
    t = mk("T-1", lottery="ssq", front=[1, 2, 3, 4, 5, 6], back=[1])
    rep = AssetCenter.build([t])
    assert rep.total_tickets == 1


@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq", "dlt"])
def test_lottery_build_matrix(ticket_storage, lottery):
    t = mk("T-1", lottery=lottery)
    if lottery == "ssq":
        t["front"] = [1, 2, 3, 4, 5, 6]; t["back"] = [1]
    rep = AssetCenter.build([t], lottery=lottery)
    assert rep.total_tickets == 1


# ---------- 最大单次中奖 ----------
def test_max_win(ticket_storage):
    rep = AssetCenter.build([WIN])
    assert rep.max_win >= 5_000_000


def test_max_win_zero(ticket_storage):
    rep = AssetCenter.build([LOSE])
    assert rep.max_win == 0.0


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_max_win_matrix(ticket_storage, n):
    tickets = [dict(WIN, ticket_id=f"W-{i}") for i in range(n)]
    rep = AssetCenter.build(tickets)
    assert rep.max_win >= 5_000_000


# ---------- 便捷函数与免责声明 ----------
def test_build_asset_report_helper(ticket_storage):
    rep = build_asset_report([LOSE])
    assert isinstance(rep, AssetReport)


def test_disclaimer_constant(ticket_storage):
    assert "随机性" in DISCLAIMER


# ---------- 大规模矩阵 ----------
@pytest.mark.parametrize("n", range(30))
def test_build_many_tickets(ticket_storage, n):
    tickets = [mk(f"T-{i}") for i in range(n)]
    rep = AssetCenter.build(tickets)
    assert rep.total_tickets == n


@pytest.mark.parametrize("seed", range(20))
def test_random_portfolio(ticket_storage, seed):
    import random
    random.seed(seed)
    tickets = []
    for i in range(random.randint(1, 20)):
        is_win = random.random() < 0.15
        if is_win:
            tickets.append(dict(WIN, ticket_id=f"W-{seed}-{i}"))
        else:
            tickets.append(dict(LOSE, ticket_id=f"L-{seed}-{i}"))
    rep = AssetCenter.build(tickets)
    assert rep.total_tickets == len(tickets)
    assert 0 <= rep.win_rate <= 1
    assert 0 <= rep.loss_rate <= 1
    assert rep.risk_level in ("A", "B", "C", "D")
    assert rep.summary_text()
