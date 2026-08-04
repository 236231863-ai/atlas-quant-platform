"""v4.6 P4：自动兑奖体验优化测试。

覆盖：首页兑奖汇总（待开奖/已中奖/待领取）/ 卡片 / 状态机。
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from pages.dashboard_page import DashboardPage  # noqa: E402
from engine.claim_center import ClaimCenter, ClaimItem  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _add_ticket(lottery="dlt", front=None, back=None, draw_date="2026-08-01"):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    return mgr.add(lottery, front or [1, 2, 3, 4, 5], back or [1, 2],
                   buy_date="2026-07-31", draw_date=draw_date)


def _summary(qapp):
    return DashboardPage()._claim_summary()


# ---------- 汇总计算 ----------
def test_empty_summary(ticket_storage, qapp):
    s = _summary(qapp)
    assert s["waiting"] == 0
    assert s["won"] == 0
    assert s["pending_amount"] == 0.0


def test_waiting_count(ticket_storage, qapp):
    _add_ticket(draw_date=(date.today() + timedelta(days=1)).isoformat())
    s = _summary(qapp)
    assert s["waiting"] == 1


def test_no_win(ticket_storage, qapp):
    _add_ticket(draw_date="2026-08-01")
    s = _summary(qapp)
    assert s["won"] == 0
    assert s["pending_amount"] == 0.0


def test_win_ticket(ticket_storage, qapp):
    _add_ticket(front=[10, 11, 18, 22, 35], back=[6, 12], draw_date="2026-08-01")
    s = _summary(qapp)
    assert s["won"] >= 1
    assert s["pending_amount"] >= 5_000_000


def test_mixed(ticket_storage, qapp):
    _add_ticket(front=[10, 11, 18, 22, 35], back=[6, 12], draw_date="2026-08-01")
    _add_ticket(draw_date="2026-08-01")
    _add_ticket(draw_date=(date.today() + timedelta(days=1)).isoformat())
    s = _summary(qapp)
    assert s["waiting"] == 1
    assert s["won"] == 1


# ---------- 卡片 ----------
def test_card_text(ticket_storage, qapp):
    w = DashboardPage()
    card = w._claim_summary_card({"waiting": 1, "won": 0, "pending_amount": 0})
    txt = "".join(l.text() for l in card.findChildren(QLabel))
    assert "待开奖" in txt
    assert "已中奖" in txt
    assert "待领取" in txt


def test_card_instances(ticket_storage, qapp):
    w = DashboardPage()
    for s in ({"waiting": 0, "won": 0, "pending_amount": 0},
              {"waiting": 2, "won": 1, "pending_amount": 7}):
        assert w._claim_summary_card(s) is not None


def test_card_amount_format(ticket_storage, qapp):
    w = DashboardPage()
    card = w._claim_summary_card({"waiting": 0, "won": 1, "pending_amount": 7})
    txt = "".join(l.text() for l in card.findChildren(QLabel))
    assert "¥7" in txt


# ---------- ClaimCenter 状态 ----------
def test_status_waiting(ticket_storage):
    d = (date.today() + timedelta(days=1)).isoformat()
    assert ClaimCenter.status_of({"ticket_id": "T", "draw_date": d}) == "waiting_draw"


def test_status_settled(ticket_storage):
    d = (date.today() - timedelta(days=1)).isoformat()
    assert ClaimCenter.status_of({"ticket_id": "T", "draw_date": d}) == "settled_unviewed"


def test_status_claimed(ticket_storage):
    d = (date.today() - timedelta(days=1)).isoformat()
    assert ClaimCenter.status_of({"ticket_id": "T", "draw_date": d, "claimed": True}) == "claimed"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 3, 5])
def test_waiting_matrix(ticket_storage, qapp, n):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2],
                buy_date="2026-07-31",
                draw_date=(date.today() + timedelta(days=1)).isoformat())
    s = _summary(qapp)
    assert s["waiting"] == n


@pytest.mark.parametrize("i", range(10))
def test_summary_stable(ticket_storage, qapp, i):
    s = _summary(qapp)
    assert isinstance(s["waiting"], int)
    assert isinstance(s["pending_amount"], float)
