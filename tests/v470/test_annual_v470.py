"""v4.7 P3：个人彩票资产报告 2.0 测试。

覆盖：年度 ROI / 最大回撤 / 中奖分布 / 年度报告。
"""
from __future__ import annotations

import pytest

from engine.asset_center import AnnualSummary, AssetCenter


def t(tid, buy_date, cost=2.0, win=False):
    if win:
        return {"ticket_id": tid, "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": buy_date, "draw_date": "2026-08-01", "cost": cost,
                "prize_level": "一等奖"}
    return {"ticket_id": tid, "lottery": "dlt",
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": buy_date, "draw_date": "2026-08-01", "cost": cost}


# ---------- 年度 ROI ----------
def test_annual_roi():
    a = AnnualSummary(year=2026, investment=5200, winnings=860)
    assert a.net == -4340
    assert a.roi < 0


def test_annual_roi_zero():
    a = AnnualSummary(year=2026)
    assert a.roi == 0.0


def test_annual_roi_positive():
    a = AnnualSummary(year=2026, investment=100, winnings=500)
    assert a.roi > 0


# ---------- 年度报告构建 ----------
def test_annual_build():
    tickets = [t("T-1", "2026-03-05"), t("T-2", "2026-06-10")]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.investment == 4.0
    assert a.tickets == 2


def test_annual_win():
    tickets = [t("T-1", "2026-08-05", win=True)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.win_count == 1
    assert a.winnings >= 5_000_000
    assert a.prize_dist.get("一等奖", 0) == 1


def test_annual_no_win():
    tickets = [t("T-1", "2026-08-05")]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.win_count == 0
    assert a.prize_dist == {}


def test_annual_prize_dist():
    tickets = [t("T-1", "2026-08-05", win=True), t("T-2", "2026-08-06", win=True)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.prize_dist.get("一等奖", 0) == 2


# ---------- 最大回撤 ----------
def test_max_drawdown_no_win():
    """全不中：回撤 = 累计投入。"""
    tickets = [t("T-1", "2026-01-05"), t("T-2", "2026-02-05"), t("T-3", "2026-03-05")]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.max_drawdown == 6.0


def test_max_drawdown_win_resets():
    """中途中奖降低回撤。"""
    tickets = [t("T-1", "2026-01-05"), t("T-2", "2026-02-05", win=True)]
    a = AssetCenter.annual_report(tickets, 2026)
    # 前两期投入 4，中奖 500万 → 回撤大幅小于 4
    assert a.max_drawdown < 4.0


def test_max_drawdown_order():
    """回撤依赖时间顺序。"""
    tickets = [t("T-1", "2026-03-05", win=True), t("T-2", "2026-01-05")]
    a = AssetCenter.annual_report(tickets, 2026)
    # 先中奖（01月 后买 T-2？）—— 按 buy_date 排序后 T-2(01) 先
    assert a.max_drawdown >= 0


# ---------- 结构 ----------
def test_annual_to_dict():
    a = AnnualSummary(year=2026, investment=100, winnings=10)
    d = a.to_dict()
    assert "roi" in d
    assert "max_drawdown" in d
    assert "prize_dist" in d


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 5, 10])
def test_annual_scale(n):
    tickets = [t(f"T{i}", f"2026-{i % 12 + 1:02d}-05") for i in range(n)]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.tickets == n
    assert a.investment == n * 2.0


@pytest.mark.parametrize("cost", [2, 5, 10])
def test_annual_cost(cost):
    a = AssetCenter.annual_report([t("T", "2026-08-05", cost=cost)], 2026)
    assert a.investment == cost


@pytest.mark.parametrize("seed", range(10))
def test_annual_random(seed):
    import random
    random.seed(seed)
    tickets = [t(f"T{i}", f"2026-{random.randint(1, 8):02d}-{random.randint(1, 28):02d}",
                 win=random.random() < 0.2) for i in range(random.randint(1, 15))]
    a = AssetCenter.annual_report(tickets, 2026)
    assert a.max_drawdown >= 0
    assert a.roi == 0 or -1 <= a.roi  # ROI 可正可负
