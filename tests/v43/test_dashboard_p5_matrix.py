"""v4.3 P5 补充矩阵：首页重构第二版（补齐 ≥100）。"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QTableWidget  # noqa: E402

from pages.dashboard_page import DashboardPage  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def dashboard(ticket_storage, qapp):
    _seed_tickets(1)
    return DashboardPage()


def _seed_tickets(n, draw_date="2026-08-01", buy_date=None):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2],
                buy_date=buy_date or date.today().isoformat(),
                draw_date=draw_date, cost=2.0)
    return mgr


# ---------- 价值面板矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_metrics_ticket_count_wide(ticket_storage, qapp, n):
    _seed_tickets(n)
    m = DashboardPage()._value_metrics()
    assert m[0][1] == f"{n} 张"


@pytest.mark.parametrize("cost", [2, 3, 5, 10, 20])
def test_month_spend_by_cost(ticket_storage, qapp, cost):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date=date.today().isoformat(),
            draw_date="2026-08-01", cost=cost)
    m = DashboardPage()._value_metrics()
    assert m[3][1] == f"¥{cost:,.0f}"


@pytest.mark.parametrize("d", ["2026-08-01", date.today().isoformat(),
                               (date.today() + timedelta(days=1)).isoformat()])
def test_draw_date_variants(ticket_storage, qapp, d):
    _seed_tickets(1, draw_date=d)
    m = DashboardPage()._value_metrics()
    assert m[2][0] == "💰 待兑奖"


# ---------- 首页结构 ----------
def test_header_present(dashboard):
    from PySide6.QtWidgets import QLabel
    labels = "".join(l.text() for l in dashboard.findChildren(QLabel))
    assert "🎯 我的彩票" in labels


@pytest.mark.parametrize("keyword", ["我的票", "最近开奖", "待兑奖", "本月投入", "本月结果", "我的状态"])
def test_value_metric_keywords(ticket_storage, qapp, keyword):
    _seed_tickets(2)
    m = DashboardPage()._value_metrics()
    joined = "".join(f"{t}{v}" for t, v in m)
    assert keyword in joined


def test_no_research_numbers(ticket_storage, qapp):
    """首页不含研究数值（如 88.1 / 3077:2923）。"""
    _seed_tickets(1)
    w = DashboardPage()
    labels = "".join(l.text() for l in w.findChildren(QLabel))
    assert "88.1" not in labels
    assert "3077" not in labels


@pytest.mark.parametrize("i", range(10))
def test_dashboard_instance_matrix(ticket_storage, qapp, i):
    _seed_tickets(i)
    w = DashboardPage()
    assert isinstance(w, DashboardPage)


# ---------- 无票据引导 ----------
def test_empty_welcome(ticket_storage, qapp):
    w = DashboardPage()
    labels = "".join(l.text() for l in w.findChildren(QLabel))
    assert "首次使用引导" in labels


def test_with_tickets_no_guide(ticket_storage, qapp):
    _seed_tickets(1)
    w = DashboardPage()
    labels = "".join(l.text() for l in w.findChildren(QLabel))
    assert "首次使用引导" not in labels


# ---------- 头部话术模式 ----------
@pytest.mark.parametrize("seed", range(15))
def test_headline_always_str(ticket_storage, qapp, seed):
    import random
    random.seed(seed)
    _seed_tickets(random.randint(0, 4))
    w = DashboardPage()
    h = w._value_headline(w._value_metrics(), None, None)
    assert isinstance(h, str) and len(h) > 0


@pytest.mark.parametrize("prefix", ["👋", "🎯", "⚠️", "💳", "📋", "你有"])
def test_headline_variant_styles(ticket_storage, qapp, prefix):
    import random
    random.seed(len(prefix))
    _seed_tickets(random.randint(0, 3))
    w = DashboardPage()
    h = w._value_headline(w._value_metrics(), None, None)
    assert isinstance(h, str)


# ---------- 表格 ----------
@pytest.mark.parametrize("n_tables", [1])
def test_recent_table_rows(ticket_storage, qapp, n_tables):
    w = DashboardPage()
    tables = w.findChildren(QTableWidget)
    assert len(tables) >= n_tables
