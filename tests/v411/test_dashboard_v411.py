"""v4.1.1 Phase 2：首页价值重构测试。"""
from __future__ import annotations

import os
import random

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def window(app):
    from windows.main_window import MainWindow
    return MainWindow()


@pytest.fixture()
def dashboard(window, ticket_storage):
    return window.dashboard


# ---------- 6 指标 ----------
def test_six_metrics(dashboard):
    m = dashboard._value_metrics()
    assert len(m) == 6


@pytest.mark.parametrize("t", ["我的票", "最近开奖", "待兑奖", "本月投入", "本月结果", "我的状态"])
def test_metric_titles(dashboard, t):
    titles = [x for x, _ in dashboard._value_metrics()]
    assert any(t in x for x in titles)


def test_empty_metrics(dashboard):
    m = dict(dashboard._value_metrics())
    assert "0 张" in m["🎫 我的票"] or "0" in m["🎫 我的票"]


def test_my_tickets(dashboard, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(3):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date=f"2026-08-{i+1:02d}")
    m = dict(dashboard._value_metrics())
    assert "3" in m["🎫 我的票"]
    mgr.clear()


def test_pending_draw(dashboard, ticket_storage):
    from engine.ticket_system import TicketManager
    from datetime import date, timedelta
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
            buy_date=(date.today() - timedelta(days=2)).isoformat(),
            draw_date=(date.today() + timedelta(days=2)).isoformat())
    m = dict(dashboard._value_metrics())
    assert "待兑奖" in [x for x, _ in dashboard._value_metrics()][2]
    mgr.clear()


def test_month_result(dashboard, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12], buy_date="2026-07-31",
            draw_date="2026-08-01")
    m = dict(dashboard._value_metrics())
    assert "5,000,000" in m["📈 本月结果"]
    mgr.clear()


# ---------- 话术 ----------
def test_headline_no_tickets(dashboard, ticket_storage):
    from engine.ticket_system import TicketManager
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    TicketManager().clear()
    rv = PersonalReviewEngine.review([])
    b = BudgetPlanner().evaluate_tickets([])
    h = dashboard._value_headline(dashboard._value_metrics(), rv, b)
    assert "欢迎" in h


def test_headline_dynamic(dashboard, ticket_storage):
    from engine.ticket_system import TicketManager
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01",
            draw_date=(__import__('datetime').date.today().__str__() if False else "2026-08-05"))
    rv = PersonalReviewEngine.review([t.__dict__ for t in mgr.list_all()])
    b = BudgetPlanner().evaluate_tickets([t.__dict__ for t in mgr.list_all()])
    h = dashboard._value_headline(dashboard._value_metrics(), rv, b)
    assert isinstance(h, str) and len(h) > 5
    mgr.clear()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_dashboard_stability(seed, dashboard, ticket_storage):
    rng = random.Random(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(0, 10)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                draw_date="2026-08-01" if rng.random() < 0.5 else "")
    m = dashboard._value_metrics()
    assert len(m) == 6
    mgr.clear()


@pytest.mark.parametrize("seed", range(40))
def test_headline_no_crash(seed, dashboard, ticket_storage):
    rng = random.Random(1000 + seed)
    from engine.ticket_system import TicketManager
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(0, 8)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    rv = PersonalReviewEngine.review([t.__dict__ for t in mgr.list_all()])
    b = BudgetPlanner().evaluate_tickets([t.__dict__ for t in mgr.list_all()])
    h = dashboard._value_headline(dashboard._value_metrics(), rv, b)
    assert isinstance(h, str)
    mgr.clear()
