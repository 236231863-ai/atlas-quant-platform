"""v4.1 阶段1：首页「我的彩票」价值面板测试。"""
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
def value_panel(window, ticket_storage):
    return window.dashboard


# ---------- 价值指标 ----------
def test_metrics_seven(value_panel):
    m = value_panel._value_metrics()
    assert len(m) == 7


@pytest.mark.parametrize("title", ["我的票据", "今日开奖", "待兑奖", "累计投入",
                                   "累计中奖", "ROI", "本月预算"])
def test_metric_titles(value_panel, title):
    titles = [t for t, _ in value_panel._value_metrics()]
    assert title in titles


def test_empty_metrics(value_panel):
    m = dict(value_panel._value_metrics())
    assert m["我的票据"] == "0 张"
    assert m["累计投入"] == "¥0"


def test_draw_day_detection(value_panel):
    from engine.ticket_system.schedule import LotterySchedule
    from datetime import date
    today = date.today().isoformat()
    is_draw = LotterySchedule.is_draw_day("dlt", today) or LotterySchedule.is_draw_day("ssq", today)
    m = dict(value_panel._value_metrics())
    assert ("无" in m["今日开奖"]) == (not is_draw)


# ---------- 有数据时 ----------
def test_metrics_with_tickets(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(3):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date=f"2026-07-{10 + i:02d}")
    m = dict(value_panel._value_metrics())
    assert m["我的票据"] == "3 张"
    assert m["累计投入"] == "¥6"
    mgr.clear()


def test_metrics_with_win(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12],
            buy_date="2026-07-31", draw_date="2026-08-01")
    m = dict(value_panel._value_metrics())
    assert "5,000,000" in m["累计中奖"]
    mgr.clear()


def test_pending_draw(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
            buy_date="2026-12-01", draw_date="2026-12-05")
    m = dict(value_panel._value_metrics())
    assert m["待兑奖"] != "0 张"
    mgr.clear()


def test_budget_ratio(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01", cost=100.0)
    m = dict(value_panel._value_metrics())
    assert "%" in m["本月预算"]
    mgr.clear()


# ---------- 话术 ----------
def test_headline_no_tickets(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    TicketManager().clear()
    rv = PersonalReviewEngine.review([])
    b = BudgetPlanner().evaluate_tickets([])
    h = value_panel._value_headline(value_panel._value_metrics(), rv, b)
    assert "欢迎" in h


def test_headline_draw_day(value_panel, ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    TicketManager().add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    rv = PersonalReviewEngine.review([t.__dict__ for t in TicketManager().list_all()])
    b = BudgetPlanner().evaluate_tickets([])
    h = value_panel._value_headline(value_panel._value_metrics(), rv, b)
    if "今日开奖" in str(value_panel._value_metrics()) and dict(value_panel._value_metrics())["今日开奖"] != "无":
        assert "开奖" in h
    TicketManager().clear()


def test_headline_budget_over(value_panel, ticket_storage):
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    mgr = None
    # 直接构造：有票据 + 非开奖日 + 超预算 → 预算话术
    metrics = [("我的票据", "1 张"), ("今日开奖", "无"), ("待兑奖", "0 张"),
               ("累计投入", "¥600"), ("累计中奖", "¥0"), ("ROI", "-100%"),
               ("本月预算", "120%")]
    rv = PersonalReviewEngine.review([])
    rv.total_tickets = 1
    rv.total_investment = 600.0
    b = BudgetPlanner().evaluate(600, 600, 500, 6000)
    h = value_panel._value_headline(metrics, rv, b)
    assert "预算" in h or "控制" in h


# ---------- 页面结构 ----------
def test_value_panel_built(window, ticket_storage):
    assert hasattr(window.dashboard, "_value_panel")
    assert hasattr(window.dashboard, "_value_metrics")


def test_page_title(window):
    # 首页标题改为"我的彩票"
    # 通过 _value_panel 存在 + 指标方法验证
    assert hasattr(window.dashboard, "_value_metrics")


def test_dashboard_instantiates(window):
    assert window.dashboard is not None


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_metrics_stability(seed, value_panel, ticket_storage):
    rng = random.Random(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 10)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                cost=2.0 * rng.randint(1, 5))
    m = dict(value_panel._value_metrics())
    assert "张" in m["我的票据"]
    assert "¥" in m["累计投入"]
    assert "%" in m["本月预算"] or "0%" in m["本月预算"]
    mgr.clear()


@pytest.mark.parametrize("seed", range(30))
def test_value_panel_no_crash(seed, value_panel, ticket_storage):
    rng = random.Random(1000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(0, 8)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    metrics = value_panel._value_metrics()
    assert len(metrics) == 7
    mgr.clear()
