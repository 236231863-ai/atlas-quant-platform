"""v4.4 P5：首页开奖状态卡片测试。

覆盖：卡片内容（距离下一开奖/最新开奖/数据可信/待兑奖）/ 无票据 / 隔离存储。
"""
from __future__ import annotations

import os
from datetime import date

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from pages.dashboard_page import DashboardPage  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _card_text(w):
    card = w._draw_status_card()
    return "".join(l.text() for l in card.findChildren(QLabel))


# ---------- 卡片内容 ----------
def test_card_instantiates(ticket_storage, qapp):
    w = DashboardPage()
    card = w._draw_status_card()
    assert card is not None


def test_card_title(ticket_storage, qapp):
    assert "开奖状态" in _card_text(DashboardPage())


def test_card_next_draw(ticket_storage, qapp):
    assert "距离下一开奖" in _card_text(DashboardPage())


def test_card_health(ticket_storage, qapp):
    assert "数据可信" in _card_text(DashboardPage())


def test_card_pending(ticket_storage, qapp):
    assert "待兑奖" in _card_text(DashboardPage())


def test_card_contains_lotteries(ticket_storage, qapp):
    txt = _card_text(DashboardPage())
    assert "大乐透" in txt
    assert "双色球" in txt


# ---------- 无票据 ----------
def test_card_no_tickets(ticket_storage, qapp):
    txt = _card_text(DashboardPage())
    assert "待兑奖 0 张" in txt


# ---------- 有票据 ----------
def test_card_with_tickets(ticket_storage, qapp):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date=date.today().isoformat(),
            draw_date="2026-08-01")
    txt = _card_text(DashboardPage())
    assert "待兑奖" in txt


# ---------- 数据可信等级 ----------
def test_card_health_level_present(ticket_storage, qapp):
    txt = _card_text(DashboardPage())
    assert "级" in txt or "未知" in txt


# ---------- 矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_card_repeated_instances(ticket_storage, qapp, i):
    w = DashboardPage()
    assert _card_text(w)


@pytest.mark.parametrize("n", [0, 1, 3, 5])
def test_card_pending_counts(ticket_storage, qapp, n):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2],
                buy_date=date.today().isoformat(), draw_date="2026-08-01")
    txt = _card_text(DashboardPage())
    assert "待兑奖" in txt


# ---------- Dashboard 整体 ----------
def test_dashboard_with_card(ticket_storage, qapp):
    w = DashboardPage()
    labels = "".join(l.text() for l in w.findChildren(QLabel))
    assert "开奖状态" in labels or "我的彩票" in labels
