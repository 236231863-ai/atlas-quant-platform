"""v4.0.0 Phase 3：历史投注复盘测试。"""
from __future__ import annotations

import random

import pytest

from engine.personal_review import (
    PersonalReviewEngine,
    PersonalReviewReport,
    review_tickets,
)

# 26086 期开奖：10 11 18 22 35 + 06 12
WIN_FRONT = [10, 11, 18, 22, 35]
WIN_BACK = [6, 12]


def _tk(front, back, buy="2026-07-31", draw="2026-08-01", lottery="dlt", cost=2.0):
    return {"lottery": lottery, "front": front, "back": back,
            "buy_date": buy, "draw_date": draw, "cost": cost}


# ---------- 空数据 ----------
def test_empty():
    r = review_tickets([])
    assert r.total_tickets == 0
    assert r.total_investment == 0
    assert r.win_count == 0


def test_empty_type():
    assert isinstance(review_tickets([]), PersonalReviewReport)


# ---------- 投入统计 ----------
def test_investment_single():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert r.total_tickets == 1
    assert r.total_investment == 2.0


def test_investment_multi():
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7], cost=2.0),
               _tk([6, 7, 8, 9, 10], [8, 9], cost=4.0)]
    r = review_tickets(tickets)
    assert r.total_investment == 6.0


@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_ticket_count(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7], cost=2.0) for _ in range(n)]
    r = review_tickets(tickets)
    assert r.total_tickets == n
    assert r.total_investment == 2.0 * n


# ---------- 中奖匹配 ----------
def test_first_prize():
    r = review_tickets([_tk(WIN_FRONT, WIN_BACK)])
    assert r.win_count == 1
    assert r.total_winnings == 5_000_000


def test_no_win():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert r.win_count == 0
    assert r.total_winnings == 0


def test_minor_win():
    # 后区全中（0+2）→ 九等奖 5 元
    r = review_tickets([_tk([1, 2, 3, 4, 5], WIN_BACK)])
    assert r.win_count == 1
    assert r.total_winnings == 5


def test_five_zero_win():
    # 前区全中（5+0）→ 三等奖 1 万
    r = review_tickets([_tk(WIN_FRONT, [1, 2])])
    assert r.total_winnings == 10_000


@pytest.mark.parametrize("front,back,amount", [
    (WIN_FRONT, WIN_BACK, 5_000_000),   # 一等奖
    (WIN_FRONT, [6, 1], 180_000),        # 二等奖
    (WIN_FRONT, [1, 2], 10_000),         # 三等奖
    ([10, 11, 18, 22, 1], WIN_BACK, 3_000),  # 四等奖
    ([1, 2, 3, 4, 5], WIN_BACK, 5),      # 九等奖(0+2)
    ([1, 2, 3, 4, 5], [7, 8], 0),        # 未中
])
def test_prize_amounts(front, back, amount):
    r = review_tickets([_tk(front, back)])
    assert r.total_winnings == amount


# ---------- 净收益/ROI ----------
def test_net_profit():
    r = review_tickets([_tk(WIN_FRONT, [1, 2])])  # 中 1 万，投入 2
    assert r.net_profit == 10_000 - 2


def test_net_profit_loss():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])  # 未中
    assert r.net_profit == -2.0


def test_roi_negative():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert r.roi == -1.0


def test_roi_positive():
    r = review_tickets([_tk(WIN_FRONT, WIN_BACK)])
    assert r.roi > 0


def test_win_rate():
    tickets = [_tk(WIN_FRONT, WIN_BACK), _tk([1, 2, 3, 4, 5], [6, 7])]
    r = review_tickets(tickets)
    assert r.win_rate == pytest.approx(0.5)


# ---------- 月度趋势 ----------
def test_monthly_trend():
    t1 = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-06-10", draw="2026-06-13")
    t2 = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-07-05", draw="2026-07-08")
    r = review_tickets([t1, t2])
    assert r.monthly_trend["2026-06"] == pytest.approx(2.0)
    assert r.monthly_trend["2026-07"] == pytest.approx(2.0)


def test_peak_month():
    t1 = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-06-10")
    t2 = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-07-05")
    t3 = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-07-12")
    r = review_tickets([t1, t2, t3])
    assert r.peak_month == "2026-07"


def test_monthly_trend_empty():
    r = review_tickets([])
    assert r.monthly_trend == {}


# ---------- 防穿越 ----------
def test_no_time_travel():
    """指定日期未匹配到开奖 → 不穿越历史。"""
    t = _tk(WIN_FRONT, WIN_BACK, buy="2020-01-01", draw="2020-01-02")
    r = review_tickets([t])
    assert r.win_count == 0  # 2020 年无开奖记录


# ---------- review_from_manager ----------
def test_review_from_manager(task_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", WIN_FRONT, WIN_BACK, buy_date="2026-07-31", draw_date="2026-08-01")
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-20")
    r = PersonalReviewEngine.review_from_manager(mgr)
    assert r.total_tickets == 2
    assert r.win_count >= 1
    mgr.clear()


# ---------- 报告结构 ----------
def test_report_fields():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    for f in ("total_tickets", "total_investment", "total_winnings",
              "win_count", "net_profit", "roi", "monthly_trend", "peak_month"):
        assert hasattr(r, f)


@pytest.mark.parametrize("f", ["total_tickets", "total_investment",
                               "total_winnings", "net_profit", "roi"])
def test_report_dict_keys(f):
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert f in r.to_dict()


def test_summary_fields():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    t = r.summary_text()
    for kw in ("总投入", "总中奖", "净收益", "投入收益比", "中奖率"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert "随机性" in r.disclaimer
    assert "不能预测" in r.disclaimer


def test_summary_has_disclaimer():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert "随机性" in r.summary_text()


def test_loss_hint():
    r = review_tickets([_tk([1, 2, 3, 4, 5], [6, 7])])
    assert "负期望" in r.summary_text()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_review_matrix(seed):
    rng = random.Random(seed)
    tickets = []
    for _ in range(rng.randint(1, 10)):
        front = sorted(rng.sample(range(1, 36), 5))
        back = sorted(rng.sample(range(1, 13), 2))
        tickets.append(_tk(front, back, buy=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                           cost=2.0 * rng.randint(1, 3)))
    r = review_tickets(tickets)
    assert r.total_tickets == len(tickets)
    assert r.total_investment > 0
    assert r.net_profit == pytest.approx(r.total_winnings - r.total_investment, abs=0.01)


@pytest.mark.parametrize("seed", range(30))
def test_win_count_bounded(seed):
    rng = random.Random(1000 + seed)
    tickets = []
    for _ in range(rng.randint(1, 8)):
        if rng.random() < 0.5:
            tickets.append(_tk(WIN_FRONT, WIN_BACK))
        else:
            tickets.append(_tk(sorted(rng.sample(range(1, 36), 5)),
                               sorted(rng.sample(range(1, 13), 2))))
    r = review_tickets(tickets)
    assert 0 <= r.win_count <= len(tickets)
    assert 0 <= r.win_rate <= 1


@pytest.mark.parametrize("seed", range(30))
def test_roi_range(seed):
    rng = random.Random(2000 + seed)
    tickets = [_tk(sorted(rng.sample(range(1, 36), 5)),
                   sorted(rng.sample(range(1, 13), 2))) for _ in range(rng.randint(1, 6))]
    r = review_tickets(tickets)
    assert r.roi >= -1.0  # 最多全亏


@pytest.mark.parametrize("seed", range(30))
def test_monthly_trend_valid(seed):
    rng = random.Random(3000 + seed)
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}") for _ in range(5)]
    r = review_tickets(tickets)
    assert sum(r.monthly_trend.values()) == pytest.approx(r.total_investment, abs=0.01)


@pytest.mark.parametrize("seed", range(30))
def test_ssq_review(seed):
    rng = random.Random(4000 + seed)
    tickets = [{"lottery": "ssq", "front": sorted(rng.sample(range(1, 34), 6)),
                "back": [rng.randint(1, 16)], "buy_date": "2026-07-20",
                "draw_date": "2026-07-21", "cost": 2.0} for _ in range(5)]
    r = review_tickets(tickets)
    assert r.total_tickets == 5
    assert r.total_investment == 10.0


@pytest.mark.parametrize("seed", range(40))
def test_review_consistency(seed):
    rng = random.Random(5000 + seed)
    tickets = []
    for _ in range(rng.randint(2, 8)):
        if rng.random() < 0.3:
            tickets.append(_tk(WIN_FRONT, WIN_BACK))
        else:
            tickets.append(_tk(sorted(rng.sample(range(1, 36), 5)),
                               sorted(rng.sample(range(1, 13), 2))))
    r = review_tickets(tickets)
    assert r.net_profit == pytest.approx(r.total_winnings - r.total_investment, abs=0.01)
    exact = sum(1 for t in tickets if t["front"] == WIN_FRONT and t["back"] == WIN_BACK)
    assert r.win_count >= exact  # 至少包含完全匹配的
    assert r.win_count <= len(tickets)


@pytest.mark.parametrize("seed", range(40))
def test_peak_month_matrix(seed):
    rng = random.Random(6000 + seed)
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}") for _ in range(6)]
    r = review_tickets(tickets)
    if r.monthly_trend:
        assert r.peak_month in r.monthly_trend


@pytest.mark.parametrize("seed", range(30))
def test_no_date_tickets(seed):
    rng = random.Random(7000 + seed)
    tickets = [{"lottery": "dlt", "front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)), "cost": 2.0} for _ in range(5)]
    r = review_tickets(tickets)
    assert r.total_tickets == 5
    assert r.total_investment == 10.0
    assert r.monthly_trend == {}  # 无日期不计入趋势
