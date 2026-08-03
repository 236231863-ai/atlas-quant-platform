"""v4.2 Phase 2：自动复盘系统测试（200 场景）。"""
from __future__ import annotations

import random
from datetime import date

import pytest

from engine.auto_review import AutoReviewEngine, AutoReviewReport, auto_review

# 已知开奖：2026-08-01 大乐透 = [10,11,18,22,35] + [6,12]
D_DRAW = "2026-08-01"
D_FRONT = [10, 11, 18, 22, 35]
D_BACK = [6, 12]
# 2026-07-29 大乐透 = [3,4,14,28,31] + [5,7]
D2_DRAW = "2026-07-29"


def _tk(lottery="dlt", front=None, back=None, buy="", draw="", cost=2.0):
    return {
        "lottery": lottery,
        "front": front or [1, 2, 3, 4, 5],
        "back": back or [6, 7],
        "buy_date": buy,
        "draw_date": draw,
        "cost": cost,
    }


def _win_tk():
    return _tk(front=D_FRONT, back=D_BACK, buy="2026-07-31", draw=D_DRAW)


def _miss_tk():
    return _tk(draw=D_DRAW)


# ---------- 基础 ----------
def test_empty_report():
    r = AutoReviewEngine.build([], "dlt", D_DRAW)
    assert r.participated is False
    assert r.ticket_count == 0
    assert r.total_winnings == 0
    assert r.lottery_name == "大乐透"


def test_report_type():
    r = auto_review([], "dlt", D_DRAW)
    assert isinstance(r, AutoReviewReport)


def test_no_participation_no_disturb():
    tickets = [_tk(draw=D2_DRAW)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.participated is False


def test_single_miss():
    r = AutoReviewEngine.build([_miss_tk()], "dlt", D_DRAW)
    assert r.participated
    assert r.ticket_count == 1
    assert r.win_tickets == 0
    assert r.total_winnings == 0


def test_single_win():
    r = AutoReviewEngine.build([_win_tk()], "dlt", D_DRAW)
    assert r.win_tickets == 1
    assert r.total_winnings == 5_000_000


def test_mixed_win_miss():
    r = AutoReviewEngine.build([_win_tk(), _miss_tk()], "dlt", D_DRAW)
    assert r.ticket_count == 2
    assert r.win_tickets == 1
    assert r.total_winnings == 5_000_000
    assert len(r.per_ticket) == 2


def test_total_stake():
    r = AutoReviewEngine.build([_win_tk(), _tk(draw=D_DRAW, cost=5.0)], "dlt", D_DRAW)
    assert r.total_stake == 7.0


@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 12])
def test_ticket_count_matrix(n):
    tickets = [_tk(draw=D_DRAW) for _ in range(n)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == n
    assert len(r.per_ticket) == n


# ---------- 购买日期推导 ----------
def test_derived_from_buy_date():
    t = _tk(front=D_FRONT, back=D_BACK, buy="2026-07-30", draw="")
    r = AutoReviewEngine.build([t], "dlt", D_DRAW)
    assert r.participated
    assert r.win_tickets == 1


def test_derived_not_matching_other_draw():
    t = _tk(front=D_FRONT, back=D_BACK, buy="2026-07-30", draw="")
    r = AutoReviewEngine.build([t], "dlt", D2_DRAW)
    assert r.participated is False


def test_derived_multi():
    tickets = [
        _tk(front=D_FRONT, back=D_BACK, buy="2026-07-30", draw=""),
        _tk(buy="2026-07-30", draw=""),
    ]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == 2
    assert r.win_tickets == 1


@pytest.mark.parametrize("buy,participated", [
    ("2026-07-30", True),   # 周四 → 周六 08-01
    ("2026-07-27", False),  # 周一 → 周三 07-29
    ("2026-07-29", False),  # 周三开奖日 → 当期 07-29
    ("2026-08-01", True),   # 周六开奖日当天
])
def test_derived_matrix(buy, participated):
    t = _tk(buy=buy, draw="")
    r = AutoReviewEngine.build([t], "dlt", D_DRAW)
    assert r.participated == participated


# ---------- 彩种隔离 ----------
def test_lottery_isolation():
    tickets = [_tk(lottery="ssq", draw=D_DRAW), _tk(draw=D_DRAW)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == 1
    assert r.lottery == "dlt"


def test_ssq_review():
    # 双色球 2026-07-30 开奖 = [4,6,10,18,23,31] + [11]
    t = _tk(lottery="ssq", front=[4, 6, 10, 18, 23, 31], back=[11], draw="2026-07-30")
    r = AutoReviewEngine.build([t], "ssq", "2026-07-30")
    assert r.lottery_name == "双色球"
    assert r.participated
    assert r.win_tickets == 1


# ---------- 多期隔离 ----------
def test_draw_isolation():
    tickets = [_win_tk(), _tk(draw=D2_DRAW)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == 1
    assert r.win_tickets == 1


@pytest.mark.parametrize("n_other", [1, 3, 5])
def test_other_draws_excluded(n_other):
    tickets = [_win_tk()] + [_tk(draw=D2_DRAW) for _ in range(n_other)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == 1


# ---------- 本月投入 ----------
def test_month_investment():
    tickets = [
        _tk(buy=f"2026-08-{i + 1:02d}", draw="", cost=10.0) for i in range(3)
    ] + [_tk(buy="2026-07-01", draw="", cost=999.0)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.month_investment == 30.0


@pytest.mark.parametrize("n", [0, 1, 4, 8])
def test_month_investment_matrix(n):
    tickets = [_tk(buy="2026-08-01", draw="", cost=5.0) for _ in range(n)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.month_investment == 5.0 * n


# ---------- 历史中奖 ----------
def test_history_win_count():
    tickets = [_win_tk()] + [_miss_tk() for _ in range(3)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.history_win_count >= 1


def test_history_win_count_empty():
    r = AutoReviewEngine.build([_miss_tk()], "dlt", D_DRAW)
    assert r.history_win_count == 0


@pytest.mark.parametrize("wins", [0, 1, 2, 4])
def test_history_win_count_matrix(wins):
    tickets = [_win_tk() for _ in range(wins)]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.history_win_count == wins


# ---------- 话术 ----------
def test_notify_text_template():
    r = AutoReviewEngine.build([_win_tk(), _miss_tk()], "dlt", D_DRAW)
    s = r.notify_text()
    assert "2张大乐透已开奖" in s
    assert "中奖" in s
    assert "本月累计投入" in s
    assert "历史中奖" in s


def test_notify_text_no_win():
    r = AutoReviewEngine.build([_miss_tk()], "dlt", D_DRAW)
    s = r.notify_text()
    assert "未中奖" in s
    assert "中奖1注" not in s


def test_notify_text_no_induction():
    r = AutoReviewEngine.build([_win_tk()], "dlt", D_DRAW)
    s = r.notify_text()
    for bad in ("稳赚", "必中", "保证", "预测", "推荐", "提高中奖"):
        assert bad not in s


def test_summary_text_has_draw_numbers():
    # 开奖号码通过字段展示（draw_front）
    r = AutoReviewEngine.build([_miss_tk()], "dlt", D_DRAW)
    assert r.draw_front == D_FRONT
    assert r.draw_back == D_BACK
    # 参与时展示参与票据明细
    s = r.summary_text()
    assert "01 02 03 04 05" in s  # 参与票据号码展示
    # 无参与时展示开奖号码
    r2 = AutoReviewEngine.build([], "dlt", D_DRAW)
    assert "10" in r2.summary_text() and "35" in r2.summary_text()


def test_summary_no_participation():
    r = AutoReviewEngine.build([], "dlt", D_DRAW)
    s = r.summary_text()
    assert "没有你的票据" in s


# ---------- check_draws ----------
def test_check_draws_participated():
    r = AutoReviewEngine.check_draws([_win_tk()])
    assert len(r) >= 1
    assert any(x.lottery == "dlt" and x.participated for x in r)


def test_check_draws_no_tickets():
    assert AutoReviewEngine.check_draws([]) == []


@pytest.mark.parametrize("seed", range(15))
def test_check_draws_matrix(seed):
    rng = random.Random(seed)
    tickets = [_tk(draw=D_DRAW) for _ in range(rng.randint(0, 5))]
    reports = AutoReviewEngine.check_draws(tickets)
    assert isinstance(reports, list)
    for r in reports:
        assert r.participated


# ---------- to_dict ----------
def test_to_dict_keys():
    r = AutoReviewEngine.build([_win_tk()], "dlt", D_DRAW)
    d = r.to_dict()
    assert set(d) >= {"lottery", "lottery_name", "draw_date", "ticket_count",
                      "win_tickets", "total_stake", "total_winnings",
                      "month_investment", "history_win_count", "disclaimer"}


def test_to_dict_roundtrip():
    r = AutoReviewEngine.build([_win_tk()], "dlt", D_DRAW)
    d = r.to_dict()
    assert d["win_tickets"] == 1
    assert d["total_winnings"] == 5_000_000
    assert len(d["per_ticket"]) == 1


# ---------- 免责 ----------
def test_disclaimer():
    r = AutoReviewEngine.build([], "dlt", D_DRAW)
    assert "随机性" in r.disclaimer
    assert "不预测" in r.disclaimer


# ---------- 大规模随机矩阵 ----------
@pytest.mark.parametrize("seed", range(80))
def test_review_random_matrix(seed):
    rng = random.Random(seed)
    tickets = []
    n = rng.randint(0, 10)
    for _ in range(n):
        win = rng.random() < 0.3
        draw = D_DRAW if rng.random() < 0.7 else D2_DRAW
        if win:
            tickets.append(_tk(front=D_FRONT, back=D_BACK, buy="2026-07-31",
                               draw=draw, cost=rng.randint(2, 20)))
        else:
            tickets.append(_tk(draw=draw, cost=rng.randint(2, 20)))
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.ticket_count == sum(1 for t in tickets if t["draw_date"] == D_DRAW)
    assert r.win_tickets <= r.ticket_count
    assert len(r.per_ticket) == r.ticket_count
    assert r.total_stake >= 0
    assert r.total_winnings == r.win_tickets * 5_000_000
    assert r.notify_text()


@pytest.mark.parametrize("seed", range(30))
def test_review_mixed_lotteries(seed):
    rng = random.Random(1000 + seed)
    tickets = []
    for _ in range(rng.randint(0, 8)):
        lot = "dlt" if rng.random() < 0.5 else "ssq"
        draw = D_DRAW if lot == "dlt" else "2026-08-02"
        if lot == "dlt" and rng.random() < 0.4:
            tickets.append(_tk(lottery="dlt", front=D_FRONT, back=D_BACK, draw=draw))
        else:
            tickets.append(_tk(lottery=lot, draw=draw))
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.participated == any(t["lottery"] == "dlt" and t["draw_date"] == D_DRAW for t in tickets)
    assert r.lottery_name == "大乐透"
    assert r.notify_text()


@pytest.mark.parametrize("seed", range(30))
def test_review_notify_stability(seed):
    rng = random.Random(2000 + seed)
    tickets = [_tk(draw=D_DRAW, cost=rng.randint(2, 10)) for _ in range(rng.randint(1, 6))]
    if rng.random() < 0.5:
        tickets.append(_win_tk())
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    s = r.notify_text()
    assert isinstance(s, str) and len(s) > 5
    # 无诱导
    for bad in ("稳赚", "必中", "保证", "推荐", "提高中奖"):
        assert bad not in s


@pytest.mark.parametrize("seed", range(20))
def test_review_full_flow(seed, ticket_storage):
    """全流程：保存→自动复盘→通知。"""
    from engine.ticket_system import TicketManager
    rng = random.Random(3000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(1, 5)):
        mgr.add("dlt", D_FRONT if rng.random() < 0.3 else [1, 2, 3, 4, 5],
                D_BACK if rng.random() < 0.3 else [6, 7],
                buy_date="2026-07-31", draw_date=D_DRAW)
    tickets = [t.__dict__ for t in mgr.list_all()]
    r = AutoReviewEngine.build(tickets, "dlt", D_DRAW)
    assert r.participated
    assert r.ticket_count == len(tickets)
    assert r.notify_text()
    mgr.clear()
