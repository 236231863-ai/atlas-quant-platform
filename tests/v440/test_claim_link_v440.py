"""v4.4 P4：自动兑奖联动测试。

覆盖：run 兑奖 / on_draw_updated 事件触发 / attach 订阅 / 无票据 / 异常。
"""
from __future__ import annotations

import pytest

from engine.live_draw import (
    AutoClaimLink, ClaimLinkResult, DrawEvent, DrawEventBus, attach_auto_claim,
)


class FakeNotifier:
    def __init__(self):
        self.calls = []

    def notify(self, title, message, timeout_ms=5000):
        self.calls.append((title, message))
        return True


def mk_win_ticket(tid="T-1"):
    return {"ticket_id": tid, "lottery": "dlt", "front": [10, 11, 18, 22, 35],
            "back": [6, 12], "buy_date": "2026-07-31", "draw_date": "2026-08-01",
            "cost": 2.0, "claimed": False}


def mk_lose_ticket(tid="T-2"):
    return {"ticket_id": tid, "lottery": "dlt", "front": [1, 2, 3, 4, 5],
            "back": [1, 2], "buy_date": "2026-07-31", "draw_date": "2026-08-01",
            "cost": 2.0, "claimed": False}


# ---------- run 基本 ----------
def test_run_no_tickets(ticket_storage):
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01", tickets=[])
    assert r.matched == 0
    assert not r.has_tickets


def test_run_win(ticket_storage):
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01",
                          tickets=[mk_win_ticket()])
    assert r.matched == 1
    assert r.won == 1
    assert r.total_winnings >= 5_000_000
    assert r.reason == "ok"


def test_run_no_win(ticket_storage):
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01",
                          tickets=[mk_lose_ticket()])
    assert r.matched == 1
    assert r.won == 0


def test_run_notifier_called(ticket_storage):
    nt = FakeNotifier()
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01",
                          tickets=[mk_win_ticket()], notifier=nt)
    assert r.notified is True
    assert len(nt.calls) >= 1


def test_run_result_dict(ticket_storage):
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01",
                          tickets=[mk_lose_ticket()])
    d = r.to_dict()
    assert d["lottery"] == "dlt"
    assert d["matched"] == 1


# ---------- 事件触发 ----------
def test_on_draw_updated(ticket_storage):
    ev = DrawEvent(event_type="draw_updated", lottery="dlt",
                   issue="26087", draw_date="2026-08-01")
    r = AutoClaimLink.on_draw_updated(ev)
    assert isinstance(r, ClaimLinkResult)


def test_on_draw_updated_no_issue(ticket_storage):
    ev = DrawEvent(event_type="draw_updated", lottery="dlt")
    assert AutoClaimLink.on_draw_updated(ev) is None


# ---------- attach 订阅 ----------
def test_attach_subscribes(ticket_storage):
    DrawEventBus.reset()
    attach_auto_claim()
    assert DrawEventBus.subscriber_count("draw_updated") >= 1
    DrawEventBus.reset()


def test_attach_triggered_by_event(ticket_storage):
    DrawEventBus.reset()
    attach_auto_claim()
    ev = DrawEvent(event_type="draw_updated", lottery="dlt",
                   issue="26087", draw_date="2026-08-01")
    DrawEventBus.publish(ev)  # 不应抛异常
    DrawEventBus.reset()


# ---------- 通知文本 ----------
def test_notify_text_no_tickets(ticket_storage):
    r = ClaimLinkResult(lottery="dlt", draw_date="2026-08-01")
    assert "本期无你的票据" in r.notify_text()


def test_notify_text_won(ticket_storage):
    r = ClaimLinkResult(lottery="dlt", draw_date="2026-08-01",
                        matched=2, won=1, total_winnings=5000000)
    assert "中奖 1 注" in r.notify_text()


def test_notify_text_no_win(ticket_storage):
    r = ClaimLinkResult(lottery="dlt", draw_date="2026-08-01", matched=2, won=0)
    assert "本期未中奖" in r.notify_text()


def test_disclaimer(ticket_storage):
    assert "随机性" in ClaimLinkResult().disclaimer


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n_win,n_lose", [(0, 1), (1, 0), (2, 3), (3, 2), (5, 5)])
def test_run_matrix(ticket_storage, n_win, n_lose):
    tickets = [mk_win_ticket(f"W-{i}") for i in range(n_win)] + \
              [mk_lose_ticket(f"L-{i}") for i in range(n_lose)]
    r = AutoClaimLink.run(lottery="dlt", draw_date="2026-08-01", tickets=tickets)
    assert r.matched == n_win + n_lose
    assert r.won == n_win


@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt"])
def test_run_lottery_matrix(ticket_storage, lottery):
    t = mk_lose_ticket()
    t["lottery"] = lottery
    if lottery == "ssq":
        t["front"] = [1, 2, 3, 4, 5, 6]; t["back"] = [1]
    r = AutoClaimLink.run(lottery=lottery, tickets=[t])
    assert r.reason == "ok"


@pytest.mark.parametrize("i", range(10))
def test_run_many_isolated(ticket_storage, i):
    r = AutoClaimLink.run(lottery="dlt", tickets=[])
    assert isinstance(r, ClaimLinkResult)
