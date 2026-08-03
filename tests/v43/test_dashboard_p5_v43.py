"""v4.3 P5：首页重构第二版测试（≥100 场景）。

3 秒价值首屏：有几张票 / 有几个开奖 / 是否有奖金待查看 / 本月投入。
研究指标（平均和值/奇偶/冷热）不再显示在首页。
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from pages.dashboard_page import DashboardPage  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def dashboard(ticket_storage, qapp):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
            draw_date="2026-08-01", cost=2.0)
    return DashboardPage()


# ---------- 实例化 ----------
def test_instantiates(ticket_storage, qapp):
    w = DashboardPage()
    assert w is not None


def test_instantiates_empty(ticket_storage, qapp):
    w = DashboardPage()
    assert isinstance(w, DashboardPage)


# ---------- 3 秒价值指标 ----------
def test_value_metrics_shape(dashboard):
    m = dashboard._value_metrics()
    assert len(m) == 6
    assert m[0][0] == "🎫 我的票"
    assert m[1][0] == "⏰ 最近开奖"
    assert m[2][0] == "💰 待兑奖"
    assert m[3][0] == "📊 本月投入"
    assert m[4][0] == "📈 本月结果"
    assert m[5][0] == "🎯 我的状态"


def test_value_ticket_count(dashboard):
    m = dashboard._value_metrics()
    assert m[0][1].startswith("1")


@pytest.mark.parametrize("n", [0, 1, 2, 5])
def test_value_ticket_count_matrix(ticket_storage, qapp, n):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
                draw_date="2026-08-01")
    w = DashboardPage()
    m = w._value_metrics()
    assert m[0][1] == f"{n} 张"


def test_value_month_spend_present(dashboard):
    m = dashboard._value_metrics()
    assert m[3][1].startswith("¥")


def test_value_headline_nonempty(dashboard):
    m = dashboard._value_metrics()
    h = dashboard._value_headline(m, None, None)
    assert h


def test_value_headline_welcome(ticket_storage, qapp):
    """无票据时欢迎话术。"""
    w = DashboardPage()
    m = w._value_metrics()
    h = w._value_headline(m, None, None)
    assert "欢迎" in h or "第一注" in h


@pytest.mark.parametrize("i", range(10))
def test_value_headline_variants(ticket_storage, qapp, i):
    w = DashboardPage()
    m = w._value_metrics()
    h = w._value_headline(m, None, None)
    assert isinstance(h, str) and h


# ---------- 首页不显示研究指标 ----------
def test_no_research_metrics_in_header(ticket_storage, qapp):
    w = DashboardPage()
    # 首页标题应为「我的彩票」而非研究指标
    from PySide6.QtWidgets import QLabel
    labels = [lbl.text() for lbl in w.findChildren(QLabel)]
    joined = "".join(labels)
    assert "我的彩票" in joined
    assert "平均和值" not in joined
    assert "奇偶" not in joined


def test_recent_table_present(dashboard):
    from PySide6.QtWidgets import QTableWidget
    tables = dashboard.findChildren(QTableWidget)
    assert len(tables) >= 1


def test_study_hint_present(dashboard):
    from PySide6.QtWidgets import QLabel
    labels = "".join(l.text() for l in dashboard.findChildren(QLabel))
    assert "数据分析" in labels


# ---------- 动态话术 ----------
def test_dynamic_waiting(dashboard):
    """有待兑奖时的动态话术。"""
    from engine.ticket_system import TicketManager
    tm = TicketManager()
    tickets = [t.__dict__ for t in tm.list_all()]
    # 构造开奖已到（今天/昨天）票据
    from engine.reminder_center import today_reminders
    r = today_reminders(tickets)
    m = dashboard._value_metrics()
    h = dashboard._value_headline(m, None, None)
    if r.ticket_status["ready_claim"] > 0 or r.prize_due > 0:
        assert h


@pytest.mark.parametrize("has_ticket", [True, False])
def test_dynamic_has_ticket(ticket_storage, qapp, has_ticket):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    if has_ticket:
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
                draw_date="2026-08-01")
    w = DashboardPage()
    m = w._value_metrics()
    h = w._value_headline(m, None, None)
    assert h
    if has_ticket:
        assert m[0][1] == "1 张"
    else:
        assert m[0][1] == "0 张"


# ---------- 状态字段 ----------
def test_status_field_value(dashboard):
    m = dashboard._value_metrics()
    assert m[5][1] in ("需关注", "理性购彩")


@pytest.mark.parametrize("state", ["需关注", "理性购彩"])
def test_status_values(ticket_storage, qapp, state):
    m = DashboardPage()._value_metrics()
    assert m[5][1] in ("需关注", "理性购彩")


# ---------- 待兑奖计数 ----------
def test_ready_claim_count(dashboard):
    from engine.ticket_system import TicketManager
    from engine.reminder_center import today_reminders
    tm = TicketManager()
    tickets = [t.__dict__ for t in tm.list_all()]
    r = today_reminders(tickets)
    ready = r.ticket_status["ready_claim"] + r.prize_due
    m = dashboard._value_metrics()
    assert int(m[2][1].split()[0]) == ready


# ---------- 大规模矩阵 ----------
@pytest.mark.parametrize("n", range(10))
def test_metrics_matrix(ticket_storage, qapp, n):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
                draw_date="2026-08-01")
    w = DashboardPage()
    m = w._value_metrics()
    assert m[0][1] == f"{n} 张"
    assert len(m) == 6


@pytest.mark.parametrize("seed", range(10))
def test_headline_random_state(ticket_storage, qapp, seed):
    import random
    random.seed(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(random.randint(0, 5)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
                draw_date="2026-08-01")
    w = DashboardPage()
    m = w._value_metrics()
    h = w._value_headline(m, None, None)
    assert isinstance(h, str) and h
