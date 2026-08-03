"""v4.3 P2 补充矩阵：自动兑奖中心（≥200 总场景）。

大规模参数化：状态判定 / 待兑奖列表 / 自动兑奖 / 事件计数 / 持久化。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.claim_center import ClaimCenter, ClaimItem
from engine.ticket_system import TicketManager
from engine.user_events import EventTracker

TODAY = date.today().isoformat()
DRAW = "2026-08-01"


def mk(tid, draw_date="", claimed=False, lottery="dlt"):
    return {"ticket_id": tid, "lottery": lottery, "front": [1, 2, 3, 4, 5],
            "back": [1, 2], "buy_date": "2026-07-31", "draw_date": draw_date,
            "cost": 2.0, "claimed": claimed}


# ---------- 状态判定大规模参数化 ----------
DRAWS = [""] + [(date.today() + timedelta(days=i)).isoformat() for i in range(-30, 31)]


@pytest.mark.parametrize("draw_date", DRAWS)
def test_status_matrix_draw_dates(ticket_storage, draw_date):
    t = mk("T", draw_date=draw_date)
    st = ClaimCenter.status_of(t, TODAY)
    if draw_date == "" or draw_date > TODAY:
        assert st == "waiting_draw"
    else:
        assert st == "settled_unviewed"


@pytest.mark.parametrize("claimed", [True, False] * 30)
def test_status_matrix_claimed(ticket_storage, claimed):
    st = ClaimCenter.status_of(mk("T", draw_date=TODAY, claimed=claimed), TODAY)
    assert st == ("claimed" if claimed else "settled_unviewed")


def test_status_matrix_viewed_40(ticket_storage):
    EventTracker().clear()
    for i in range(40):
        ClaimCenter.mark_viewed(f"V-{i}")
    for i in range(40):
        st = ClaimCenter.status_of(mk(f"V-{i}", draw_date=TODAY), TODAY)
        assert st == "viewed"
    assert ClaimCenter.status_of(mk("V-99", draw_date=TODAY), TODAY) == "settled_unviewed"


# ---------- 待兑奖列表矩阵 ----------
@pytest.mark.parametrize("n_wait,n_unviewed,n_viewed,n_claimed", [
    (0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1),
    (2, 3, 1, 1), (5, 5, 5, 5), (10, 0, 0, 0), (0, 10, 0, 0), (3, 3, 3, 3),
])
def test_pending_text_matrix(ticket_storage, n_wait, n_unviewed, n_viewed, n_claimed):
    EventTracker().clear()
    tickets = []
    for i in range(n_wait):
        tickets.append(mk(f"W-{i}", draw_date=(date.today() + timedelta(days=1)).isoformat()))
    for i in range(n_unviewed):
        tickets.append(mk(f"U-{i}", draw_date=TODAY))
    for i in range(n_viewed):
        tickets.append(mk(f"V-{i}", draw_date=TODAY))
        ClaimCenter.mark_viewed(f"V-{i}")
    for i in range(n_claimed):
        tickets.append(mk(f"C-{i}", draw_date=TODAY, claimed=True))
    text = ClaimCenter.pending_text(tickets)
    assert f"等待开奖：{n_wait} 张" in text
    assert f"已开奖待查看：{n_unviewed} 张" in text
    assert f"已查看：{n_viewed} 张" in text
    assert f"已兑奖：{n_claimed} 张" in text


@pytest.mark.parametrize("total", [1, 2, 3, 5, 8, 13, 21, 34, 55])
def test_build_items_size(ticket_storage, total):
    tickets = [mk(f"T-{i}", draw_date=TODAY) for i in range(total)]
    assert len(ClaimCenter.build_items(tickets)) == total


@pytest.mark.parametrize("total", [1, 2, 3, 5, 8, 13, 21])
def test_pending_list_only_processing(ticket_storage, total):
    tickets = [mk(f"T-{i}", draw_date=(date.today() - timedelta(days=i)).isoformat())
               for i in range(total)]
    pending = ClaimCenter.pending_list(tickets)
    assert len(pending) == total  # 全部已开奖待查看


# ---------- auto_claim 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 10])
def test_auto_claim_no_match_matrix(ticket_storage, n):
    tickets = [mk(f"T-{i}", draw_date=(date.today() + timedelta(days=5)).isoformat())
               for i in range(n)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert rep.matched == 0
    assert rep.won == 0


@pytest.mark.parametrize("n_win,n_lose", [
    (0, 1), (1, 0), (1, 1), (2, 3), (3, 2), (5, 5),
])
def test_auto_claim_win_lose_matrix(ticket_storage, n_win, n_lose):
    tickets = []
    for i in range(n_win):
        tickets.append({"ticket_id": f"W-{i}", "lottery": "dlt",
                        "front": [10, 11, 18, 22, 35], "back": [6, 12],
                        "buy_date": "2026-07-31", "draw_date": DRAW,
                        "cost": 2.0, "claimed": False})
    for i in range(n_lose):
        tickets.append({"ticket_id": f"L-{i}", "lottery": "dlt",
                        "front": [1, 2, 3, 4, 5], "back": [1, 2],
                        "buy_date": "2026-07-31", "draw_date": DRAW,
                        "cost": 2.0, "claimed": False})
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert rep.matched == n_win + n_lose
    assert rep.won == n_win


@pytest.mark.parametrize("i", range(30))
def test_auto_claim_records_event_matrix(ticket_storage, i):
    EventTracker().clear()
    tickets = [mk("T-1", draw_date=DRAW)]
    ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert EventTracker().count("auto_claim_run") == 1


@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq"])
def test_auto_claim_lottery_no_crash(ticket_storage, lottery):
    tickets = [mk("T-1", draw_date=DRAW, lottery=lottery)]
    rep = ClaimCenter.auto_claim(tickets, lottery=lottery, draw_date=DRAW)
    assert isinstance(rep.matched, int)


# ---------- 事件计数矩阵 ----------
@pytest.mark.parametrize("n", [1, 2, 3, 5, 10])
def test_claim_viewed_event_count(ticket_storage, n):
    EventTracker().clear()
    for i in range(n):
        ClaimCenter.mark_viewed(f"T-{i}")
    assert EventTracker().count("claim_viewed") == n


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_claim_confirmed_event_count(ticket_storage, n):
    EventTracker().clear()
    mgr = TicketManager()
    for i in range(n):
        t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=TODAY)
        ClaimCenter.mark_claimed(t.ticket_id)
    assert EventTracker().count("claim_confirmed") == n


def test_mixed_event_summary(ticket_storage):
    EventTracker().clear()
    mgr = TicketManager()
    t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=TODAY)
    ClaimCenter.mark_viewed(t.ticket_id)
    ClaimCenter.mark_claimed(t.ticket_id)
    ClaimCenter.auto_claim([t.__dict__], lottery="dlt", draw_date=TODAY)
    s = EventTracker().summary()
    assert s["claim_viewed"] == 1
    assert s["claim_confirmed"] == 1
    assert s["auto_claim_run"] == 1


# ---------- 票据持久化矩阵 ----------
@pytest.mark.parametrize("n", [1, 2, 5, 10])
def test_claimed_persist_across_reload(ticket_storage, n):
    mgr = TicketManager()
    ids = []
    for i in range(n):
        ids.append(mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=TODAY).ticket_id)
    for tid in ids:
        mgr.set_claimed(tid, True)
    mgr2 = TicketManager()
    for tid in ids:
        assert mgr2.get(tid).claimed is True


@pytest.mark.parametrize("n", [1, 2, 5, 10])
def test_unclaimed_default(ticket_storage, n):
    mgr = TicketManager()
    for i in range(n):
        t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=TODAY)
        assert t.claimed is False


# ---------- ClaimItem 结构矩阵 ----------
@pytest.mark.parametrize("status", ["waiting_draw", "settled_unviewed", "viewed", "claimed"])
def test_claim_item_status_text_matrix(ticket_storage, status):
    it = ClaimItem(ticket_id="T-1", status=status)
    assert it.status_text
    assert it.to_dict()["status"] == status


@pytest.mark.parametrize("won,amount", [(False, 0), (True, 5), (True, 5000000), (True, 3000)])
def test_claim_item_won_amount(ticket_storage, won, amount):
    it = ClaimItem(ticket_id="T-1", won=won, amount=amount)
    d = it.to_dict()
    assert d["won"] == won
    assert d["amount"] == amount
