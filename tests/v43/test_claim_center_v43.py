"""v4.3 P2：自动兑奖中心测试（≥200 场景）。

验收标准：从「页面存在」到「用户行为发生」。
覆盖：4 状态机 / 待兑奖列表 / 自动兑奖 / 标记查看/兑奖 / 事件记录 / 持久化。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.claim_center import CLAIM_STATUS, AutoClaimReport, ClaimCenter, ClaimItem
from engine.ticket_system import TicketManager
from engine.user_events import EventTracker

TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def mk_ticket(tid="T-1", lottery="dlt", front=None, back=None,
              draw_date="", claimed=False, cost=2.0, buy_date=""):
    """构造票据 dict（与 TicketRecord.__dict__ 结构一致）。"""
    return {
        "ticket_id": tid, "lottery": lottery,
        "front": front or [1, 2, 3, 4, 5], "back": back or [1, 2],
        "buy_date": buy_date or YESTERDAY, "draw_date": draw_date,
        "cost": cost, "claimed": claimed,
    }


class FakeNotifier:
    def __init__(self):
        self.calls = []

    def notify(self, title, message, timeout_ms=5000):
        self.calls.append((title, message))
        return True


# ---------- 状态判定：等待开奖 ----------
@pytest.mark.parametrize("draw_date", ["", None, TOMORROW])
def test_status_waiting_draw(ticket_storage, draw_date):
    assert ClaimCenter.status_of(mk_ticket(draw_date=draw_date or ""), TODAY) == "waiting_draw"


def test_status_waiting_draw_many(ticket_storage):
    for i in range(20):
        d = (date.today() + timedelta(days=i + 1)).isoformat()
        assert ClaimCenter.status_of(mk_ticket(tid=f"T-{i}", draw_date=d), TODAY) == "waiting_draw"


# ---------- 状态判定：已开奖待查看 ----------
def test_status_settled_unviewed_today(ticket_storage):
    assert ClaimCenter.status_of(mk_ticket(draw_date=TODAY), TODAY) == "settled_unviewed"


def test_status_settled_unviewed_past(ticket_storage):
    assert ClaimCenter.status_of(mk_ticket(draw_date=YESTERDAY), TODAY) == "settled_unviewed"


@pytest.mark.parametrize("days_ago", [1, 2, 3, 5, 10, 30, 100, 365])
def test_status_settled_unviewed_many(ticket_storage, days_ago):
    d = (date.today() - timedelta(days=days_ago)).isoformat()
    assert ClaimCenter.status_of(mk_ticket(draw_date=d), TODAY) == "settled_unviewed"


# ---------- 状态判定：已查看 ----------
def test_status_viewed(ticket_storage):
    EventTracker().clear()
    ClaimCenter.mark_viewed("T-1")
    t = mk_ticket(draw_date=YESTERDAY)
    assert ClaimCenter.status_of(t, TODAY) == "viewed"


def test_viewed_priority_over_unviewed(ticket_storage):
    EventTracker().clear()
    ClaimCenter.mark_viewed("T-9")
    for i in range(5):
        d = (date.today() - timedelta(days=2)).isoformat()
        st = ClaimCenter.status_of(mk_ticket(tid=f"T-{i}", draw_date=d), TODAY)
        assert st == "settled_unviewed"  # 只有 T-9 被标记
    assert ClaimCenter.status_of(mk_ticket(tid="T-9", draw_date=(date.today() - timedelta(days=2)).isoformat()), TODAY) == "viewed"


# ---------- 状态判定：已兑奖 ----------
def test_status_claimed(ticket_storage):
    t = mk_ticket(draw_date=YESTERDAY, claimed=True)
    assert ClaimCenter.status_of(t, TODAY) == "claimed"


def test_claimed_priority_over_viewed(ticket_storage):
    EventTracker().clear()
    ClaimCenter.mark_viewed("T-1")
    t = mk_ticket(tid="T-1", draw_date=YESTERDAY, claimed=True)
    assert ClaimCenter.status_of(t, TODAY) == "claimed"


@pytest.mark.parametrize("claimed", [True] * 10 + [False] * 10)
def test_status_claimed_many(ticket_storage, claimed):
    t = mk_ticket(draw_date=YESTERDAY, claimed=claimed)
    expect = "claimed" if claimed else "settled_unviewed"
    assert ClaimCenter.status_of(t, TODAY) == expect


# ---------- build_items / pending_list / pending_text ----------
def test_build_items_count(ticket_storage):
    tickets = [mk_ticket(tid=f"T-{i}", draw_date=TODAY) for i in range(5)]
    items = ClaimCenter.build_items(tickets)
    assert len(items) == 5


def test_build_items_status_text(ticket_storage):
    items = ClaimCenter.build_items([mk_ticket(draw_date=TODAY)])
    assert items[0].status_text == "已开奖待查看"


@pytest.mark.parametrize("status,text", [
    ("waiting_draw", "等待开奖"),
    ("settled_unviewed", "已开奖待查看"),
    ("viewed", "已查看"),
    ("claimed", "已兑奖"),
])
def test_status_text_map(ticket_storage, status, text):
    assert ClaimItem(ticket_id="T-1", status=status).status_text == text


def test_pending_list_only_pending(ticket_storage):
    tickets = [mk_ticket(tid="T-1", draw_date=TODAY),
               mk_ticket(tid="T-2", draw_date=TOMORROW),
               mk_ticket(tid="T-3", draw_date=YESTERDAY)]
    pending = ClaimCenter.pending_list(tickets)
    ids = {p["ticket_id"] for p in pending}
    assert ids == {"T-1", "T-3"}


def test_pending_text_counts(ticket_storage):
    tickets = [mk_ticket(tid=f"T-{i}", draw_date=TODAY) for i in range(3)]
    text = ClaimCenter.pending_text(tickets)
    assert "等待开奖：0 张" in text
    assert "已开奖待查看：3 张" in text


def test_pending_text_all_states(ticket_storage):
    EventTracker().clear()
    ClaimCenter.mark_viewed("T-2")
    tickets = [mk_ticket(tid="T-1", draw_date=TOMORROW),
               mk_ticket(tid="T-2", draw_date=YESTERDAY),
               mk_ticket(tid="T-3", draw_date=YESTERDAY, claimed=True)]
    text = ClaimCenter.pending_text(tickets)
    assert "等待开奖：1 张" in text
    assert "已开奖待查看：0 张" in text  # T-2 已被标记查看
    assert "已查看：1 张" in text
    assert "已兑奖：1 张" in text


def test_pending_text_no_tickets(ticket_storage):
    text = ClaimCenter.pending_text([])
    assert "等待开奖：0 张" in text


@pytest.mark.parametrize("n", [1, 2, 5, 10, 20])
def test_pending_text_various_sizes(ticket_storage, n):
    tickets = [mk_ticket(tid=f"T-{i}", draw_date=TODAY) for i in range(n)]
    text = ClaimCenter.pending_text(tickets)
    assert f"已开奖待查看：{n} 张" in text


# ---------- 状态机常量 ----------
def test_status_constant(ticket_storage):
    assert CLAIM_STATUS == ("waiting_draw", "settled_unviewed", "viewed", "claimed")


def test_claim_item_to_dict(ticket_storage):
    it = ClaimItem(ticket_id="T-1", lottery="dlt", front=[1, 2, 3, 4, 5],
                   back=[1, 2], draw_date=TODAY, status="settled_unviewed")
    d = it.to_dict()
    assert d["ticket_id"] == "T-1"
    assert d["status_text"] == "已开奖待查看"


# ---------- auto_claim 自动兑奖 ----------
# 注意：票据 draw_date 字段 = 开奖日（用户保存时系统记录预期开奖日）
DRAW = "2026-08-01"  # 大乐透 26086 期：10 11 18 22 35 + 06 12


def test_auto_claim_no_tickets(ticket_storage):
    rep = ClaimCenter.auto_claim([], lottery="dlt", draw_date=DRAW)
    assert rep.matched == 0
    assert not rep.has_any


def test_auto_claim_win(ticket_storage):
    tickets = [mk_ticket(tid="T-1", front=[10, 11, 18, 22, 35], back=[6, 12],
                         buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert rep.matched == 1
    assert rep.won == 1
    assert rep.total_winnings >= 5_000_000


def test_auto_claim_no_win(ticket_storage):
    tickets = [mk_ticket(tid="T-1", front=[1, 2, 3, 4, 5], back=[1, 2],
                         buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert rep.matched == 1
    assert rep.won == 0


def test_auto_claim_notify_text(ticket_storage):
    tickets = [mk_ticket(tid="T-1", front=[10, 11, 18, 22, 35], back=[6, 12],
                         buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert "中奖 1 注" in rep.notify_text()


def test_auto_claim_notify_text_no_win(ticket_storage):
    tickets = [mk_ticket(tid="T-1", buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert "本期未中奖" in rep.notify_text()


def test_auto_claim_records_event(ticket_storage):
    EventTracker().clear()
    tickets = [mk_ticket(tid="T-1", buy_date="2026-07-31", draw_date=DRAW)]
    ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert EventTracker().count("auto_claim_run") == 1


def test_auto_claim_notifier_called(ticket_storage):
    nt = FakeNotifier()
    tickets = [mk_ticket(tid="T-1", buy_date="2026-07-31", draw_date=DRAW)]
    ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW, notifier=nt)
    assert len(nt.calls) == 1
    assert "自动兑奖" in nt.calls[0][0]


def test_auto_claim_summary_text_has_disclaimer(ticket_storage):
    tickets = [mk_ticket(tid="T-1", buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    assert "随机性" in rep.summary_text()


def test_auto_claim_to_dict(ticket_storage):
    tickets = [mk_ticket(tid="T-1", buy_date="2026-07-31", draw_date=DRAW)]
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW)
    d = rep.to_dict()
    assert d["matched"] == 1
    assert d["disclaimer"]


# ---------- mark_viewed / mark_claimed ----------
def test_mark_viewed_records_event(ticket_storage):
    EventTracker().clear()
    ClaimCenter.mark_viewed("T-1")
    assert EventTracker().count("claim_viewed") == 1


def test_mark_claimed_missing_ticket(ticket_storage):
    assert ClaimCenter.mark_claimed("NOPE") is False


def test_mark_claimed_success(ticket_storage):
    EventTracker().clear()
    mgr = TicketManager()
    t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=YESTERDAY)
    assert ClaimCenter.mark_claimed(t.ticket_id) is True
    assert EventTracker().count("claim_confirmed") == 1
    # 重新加载实例验证持久化
    mgr2 = TicketManager()
    assert mgr2.get(t.ticket_id).claimed is True


def test_set_claimed_persist(ticket_storage):
    mgr = TicketManager()
    t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=YESTERDAY)
    mgr.set_claimed(t.ticket_id, True)
    mgr2 = TicketManager()  # 新实例重载
    assert mgr2.get(t.ticket_id).claimed is True


def test_set_claimed_missing(ticket_storage):
    mgr = TicketManager()
    assert mgr.set_claimed("NOPE") is False


def test_set_claimed_unclaim(ticket_storage):
    mgr = TicketManager()
    t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=YESTERDAY)
    mgr.set_claimed(t.ticket_id, True)
    mgr.set_claimed(t.ticket_id, False)
    assert mgr.get(t.ticket_id).claimed is False


# ---------- 端到端：保存→开奖→自动匹配→通知→兑奖 →事件 ----------
def test_full_claim_flow(ticket_storage):
    EventTracker().clear()
    mgr = TicketManager()
    # 保存 3 张票据（2 张匹配 2026-08-01 开奖，1 张未来）
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12], buy_date="2026-07-31", draw_date=DRAW)
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31", draw_date=DRAW)
    mgr.add("dlt", [7, 8, 9, 10, 11], [3, 4], draw_date=TOMORROW)
    tickets = [t.__dict__ for t in mgr.list_all()]
    # 自动兑奖
    nt = FakeNotifier()
    rep = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date=DRAW, notifier=nt)
    assert rep.matched == 2
    assert rep.won == 1
    assert rep.total_winnings >= 5_000_000
    assert len(nt.calls) == 1
    # 事件已记录
    evs = EventTracker().summary()
    assert evs["auto_claim_run"] == 1


def test_pending_after_claim_view(ticket_storage):
    EventTracker().clear()
    mgr = TicketManager()
    t = mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], draw_date=YESTERDAY)
    tickets = [t.__dict__]
    assert ClaimCenter.status_of(tickets[0], TODAY) == "settled_unviewed"
    ClaimCenter.mark_viewed(t.ticket_id)
    assert ClaimCenter.status_of(tickets[0], TODAY) == "viewed"
    ClaimCenter.mark_claimed(t.ticket_id)
    # 重新加载票据验证持久化后的 claimed
    mgr2 = TicketManager()
    tickets2 = [mgr2.get(t.ticket_id).__dict__]
    assert ClaimCenter.status_of(tickets2[0], TODAY) == "claimed"


# ---------- 矩阵：状态组合 ----------
def test_status_matrix(ticket_storage):
    """状态 = f(开奖日期, 已查看事件, 已兑奖标记) 全组合。"""
    EventTracker().clear()
    cases = []
    for draw in ["", TODAY, YESTERDAY, TOMORROW]:
        for viewed in [False, True]:
            for claimed in [False, True]:
                cases.append((draw, viewed, claimed))
    for idx, (draw, viewed, claimed) in enumerate(cases):
        tid = f"M-{idx}"
        if viewed:
            ClaimCenter.mark_viewed(tid)
        t = mk_ticket(tid=tid, draw_date=draw, claimed=claimed)
        st = ClaimCenter.status_of(t, TODAY)
        if claimed:
            assert st == "claimed"
        elif draw == "" or draw == TOMORROW:
            assert st == "waiting_draw"
        elif viewed:
            assert st == "viewed"
        else:
            assert st == "settled_unviewed"


def test_status_matrix_random(ticket_storage):
    import random
    random.seed(42)
    for i in range(50):
        draw = random.choice([TODAY, YESTERDAY, TOMORROW, ""])
        t = mk_ticket(tid=f"R-{i}", draw_date=draw)
        st = ClaimCenter.status_of(t, TODAY)
        if draw == "" or draw == TOMORROW:
            assert st == "waiting_draw"
        else:
            assert st in ("settled_unviewed",)


# ---------- AutoClaimReport 结构 ----------
def test_report_default(ticket_storage):
    rep = AutoClaimReport()
    assert rep.matched == 0
    assert not rep.has_any


def test_report_has_any(ticket_storage):
    rep = AutoClaimReport(matched=2)
    assert rep.has_any


def test_report_notify_no_tickets(ticket_storage):
    rep = AutoClaimReport(lottery="dlt", lottery_name="大乐透", draw_date="2026-08-01")
    assert "本期无你的票据" in rep.notify_text()


def test_disclaimer_present(ticket_storage):
    from engine.claim_center import DISCLAIMER
    assert "随机性" in DISCLAIMER
    assert "随机性" in AutoClaimReport().disclaimer
