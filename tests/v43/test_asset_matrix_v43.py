"""v4.3 P3 补充矩阵：彩票资产中心（补齐 ≥150）。"""
from __future__ import annotations

import pytest

from engine.asset_center import AssetCenter, AssetReport

DRAW = "2026-08-01"


def mk(tid, cost=2.0, buy_date="2026-07-31", lottery="dlt", win=False):
    if win:
        return {"ticket_id": tid, "lottery": lottery,
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": buy_date, "draw_date": DRAW, "cost": cost}
    return {"ticket_id": tid, "lottery": lottery,
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": buy_date, "draw_date": DRAW, "cost": cost}


# ---------- cost 边界 ----------
@pytest.mark.parametrize("cost", [0, 1, 2, 5, 10, 20, 50, 100])
def test_cost_matrix(ticket_storage, cost):
    rep = AssetCenter.build([mk("T-1", cost=cost)])
    assert rep.total_investment == cost


@pytest.mark.parametrize("costs", [[2, 2], [2, 3], [5, 10], [2] * 10, [2, 4, 6, 8, 10]])
def test_total_investment_sum(ticket_storage, costs):
    tickets = [mk(f"T-{i}", cost=c) for i, c in enumerate(costs)]
    rep = AssetCenter.build(tickets)
    assert rep.total_investment == sum(costs)


# ---------- 风险等级阈值验证 ----------
@pytest.mark.parametrize("n_lose", [1, 2, 3, 5, 10, 20, 50])
def test_loss_level_by_count(ticket_storage, n_lose):
    tickets = [mk(f"L-{i}") for i in range(n_lose)]
    rep = AssetCenter.build(tickets)
    # 全输 → 亏损率接近 100% → 高风险
    assert rep.loss_rate > 0.99
    assert rep.risk_level == "D"


def test_risk_level_scale(ticket_storage):
    """投入越大亏损额越大 → 风险等级不优于 D（全输）。"""
    for n in (1, 5, 10):
        rep = AssetCenter.build([mk(f"L-{i}") for i in range(n)])
        assert rep.risk_level == "D"


# ---------- summary_text 断言 ----------
@pytest.mark.parametrize("keyword", ["累计购买", "累计中奖", "净收益", "中奖率", "风险等级", "随机性"])
def test_summary_text_keywords(ticket_storage, keyword):
    rep = AssetCenter.build([mk("T-1"), mk("T-2")])
    assert keyword in rep.summary_text()


@pytest.mark.parametrize("n", [0, 1, 3, 7])
def test_summary_text_any_n(ticket_storage, n):
    rep = AssetCenter.build([mk(f"T-{i}") for i in range(n)])
    assert "我的彩票资产" in rep.summary_text()


# ---------- 年度报告补充 ----------
@pytest.mark.parametrize("months", [[1], [1, 2], [1, 6], [1, 2, 3, 4, 5, 6]])
def test_annual_active_months_matrix(ticket_storage, months):
    tickets = [mk(f"T-{m}", buy_date=f"2026-{m:02d}-10") for m in months]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.active_months == len(months)


@pytest.mark.parametrize("n_win,n_lose", [(0, 1), (1, 0), (2, 2), (3, 1), (0, 5)])
def test_annual_win_matrix(ticket_storage, n_win, n_lose):
    tickets = [mk(f"W-{i}", win=True) for i in range(n_win)] + \
              [mk(f"L-{i}") for i in range(n_lose)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.win_count == n_win
    assert a.tickets == n_win + n_lose


# ---------- 双彩种 ----------
def test_mixed_lottery_report(ticket_storage):
    tickets = [mk("T-1", lottery="dlt"), mk("T-2", lottery="dlt"),
               mk("T-3", lottery="ssq")]
    rep = AssetCenter.build(tickets)
    assert rep.total_tickets == 3
    assert len(rep.favorite_lotteries) >= 1


# ---------- 属性边界 ----------
def test_win_rate_cap(ticket_storage):
    rep = AssetCenter.build([mk("W-1", win=True)])
    assert rep.win_rate <= 1.0


def test_net_boundary(ticket_storage):
    rep = AssetCenter.build([mk("T-1")])
    assert rep.net == -2.0


def test_to_dict_rounded(ticket_storage):
    d = AssetCenter.build([mk("T-1")]).to_dict()
    assert isinstance(d["total_investment"], float)
    assert isinstance(d["win_rate"], float)
