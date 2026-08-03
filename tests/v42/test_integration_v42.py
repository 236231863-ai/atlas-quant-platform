"""v4.2 集成测试：数据飞轮全链路（保存→档案→提醒→复盘→健康→年度）。

把 Phase 1-6 模块串成完整用户旅程，验证数据飞轮闭环。
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.ticket_system import TicketManager
from engine.user_archive import UserArchiveEngine
from engine.reminder_center import today_reminders
from engine.auto_review import AutoReviewEngine
from engine.growth_health import GrowthHealthEngine
from engine.annual_report import AnnualReportEngine
from engine.premium import PremiumManager, PremiumPlan

JACKPOT_FRONT = [10, 11, 18, 22, 35]
JACKPOT_BACK = [6, 12]
DRAW = "2026-08-01"


def _seed_tickets(mgr, n=3, win_first=False):
    mgr.clear()
    for i in range(n):
        if win_first and i == 0:
            mgr.add("dlt", JACKPOT_FRONT, JACKPOT_BACK,
                    buy_date="2026-07-31", draw_date=DRAW, cost=2.0)
        else:
            mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                    buy_date=f"2026-08-{min(i + 1, 28):02d}", cost=2.0)
    return mgr


# ---------- 数据飞轮全链路 ----------
def test_full_flywheel(ticket_storage):
    """保存→档案→提醒→复盘→健康→年度。"""
    mgr = _seed_tickets(TicketManager(), n=3, win_first=True)
    tickets = [t.__dict__ for t in mgr.list_all()]

    # 1 档案
    arch = UserArchiveEngine.build(tickets)
    assert arch.total_tickets == 3
    assert arch.total_investment >= 6
    assert arch.win_count >= 1

    # 2 提醒
    r = today_reminders(tickets)
    assert r.ticket_status["pending_draw"] + r.ticket_status["ready_claim"] >= 1

    # 3 自动复盘
    rep = AutoReviewEngine.build(tickets, "dlt", DRAW)
    assert rep.participated
    assert rep.win_tickets >= 1

    # 4 健康指数
    h = GrowthHealthEngine.evaluate(tickets)
    assert h.rational_level in ("A", "B", "C")

    # 5 年度报告
    annual = AnnualReportEngine.build(tickets, 2026)
    assert annual.ticket_count == 3
    assert "年度总结" in annual.summary_text()
    mgr.clear()


def test_flywheel_empty(ticket_storage):
    """无数据：全模块空态不崩。"""
    mgr = TicketManager()
    mgr.clear()
    tickets = [t.__dict__ for t in mgr.list_all()]
    assert UserArchiveEngine.build(tickets).total_tickets == 0
    assert today_reminders(tickets).ticket_status["pending_draw"] == 0
    assert AutoReviewEngine.check_draws(tickets) == []
    assert GrowthHealthEngine.evaluate(tickets).rational_level == "C"
    assert AnnualReportEngine.build(tickets, 2026).ticket_count == 0
    assert PremiumManager().get_tier() in ("free", "premium")


def test_win_flows_through_all_modules(ticket_storage):
    """中奖贯穿所有模块。"""
    mgr = _seed_tickets(TicketManager(), n=1, win_first=True)
    tickets = [t.__dict__ for t in mgr.list_all()]

    arch = UserArchiveEngine.build(tickets)
    assert arch.total_winnings == 5_000_000
    assert arch.max_win == 5_000_000

    rep = AutoReviewEngine.build(tickets, "dlt", DRAW)
    assert rep.total_winnings == 5_000_000
    assert "中奖" in rep.notify_text()

    annual = AnnualReportEngine.build(tickets, 2026)
    assert annual.total_winnings == 5_000_000
    assert annual.max_win == 5_000_000
    mgr.clear()


# ---------- 模块间一致性 ----------
def test_archive_annual_consistency(ticket_storage):
    """档案与年度报告对同一数据口径一致。"""
    mgr = _seed_tickets(TicketManager(), n=4)
    tickets = [t.__dict__ for t in mgr.list_all()]
    arch = UserArchiveEngine.build(tickets)
    annual = AnnualReportEngine.build(tickets, 2026)
    assert arch.total_investment == annual.total_investment
    assert arch.win_count == annual.win_count
    mgr.clear()


def test_review_health_consistency(ticket_storage):
    """复盘与健康指数对同一已开奖票据一致。"""
    mgr = TicketManager()
    mgr.clear()
    for i in range(2):
        mgr.add("dlt", JACKPOT_FRONT, JACKPOT_BACK, buy_date="2026-07-31",
                draw_date=DRAW, cost=2.0)
    tickets = [t.__dict__ for t in mgr.list_all()]
    rep = AutoReviewEngine.build(tickets, "dlt", DRAW)
    h = GrowthHealthEngine.evaluate(tickets)
    assert rep.win_tickets == 2
    assert h.ticket_count == 2
    mgr.clear()


def test_premium_gates_annual(ticket_storage):
    """年度报告是会员功能。"""
    assert PremiumPlan.is_entitled("free", "annual_report") is False
    assert PremiumPlan.is_entitled("premium", "annual_report") is True
    m = PremiumManager()
    m.set_tier("free")
    assert m.is_allowed("annual_report") is False


# ---------- 数据飞轮增长 ----------
def test_more_data_better_value(ticket_storage):
    """数据越多，档案/报告越完整（飞轮正反馈）。"""
    mgr = TicketManager()
    mgr.clear()
    small = UserArchiveEngine.build([])
    for i in range(1, 4):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date=f"2026-{i:02d}-01", cost=5.0)
        tickets = [t.__dict__ for t in mgr.list_all()]
        arch = UserArchiveEngine.build(tickets)
        assert arch.total_tickets == i
        assert arch.purchase_months == i
    assert small.total_tickets == 0
    mgr.clear()


@pytest.mark.parametrize("seed", range(40))
def test_random_user_journey(seed, ticket_storage):
    """随机用户旅程：不同数据规模下全链路稳定。"""
    rng = random.Random(seed)
    mgr = TicketManager()
    mgr.clear()
    n = rng.randint(1, 8)
    for _ in range(n):
        win = rng.random() < 0.2
        mgr.add("dlt",
                JACKPOT_FRONT if win else [1, 2, 3, 4, 5],
                JACKPOT_BACK if win else [6, 7],
                buy_date=f"2026-{rng.randint(1, 8):02d}-{rng.randint(1, 28):02d}",
                draw_date=DRAW if win else "", cost=rng.randint(2, 10))
    tickets = [t.__dict__ for t in mgr.list_all()]

    arch = UserArchiveEngine.build(tickets)
    assert arch.total_tickets == n
    r = today_reminders(tickets)
    assert sum(r.ticket_status.values()) == n
    rep = AutoReviewEngine.build(tickets, "dlt", DRAW)
    assert rep.ticket_count <= n
    h = GrowthHealthEngine.evaluate(tickets)
    assert 0 <= h.overall_score <= 100
    annual = AnnualReportEngine.build(tickets, 2026)
    assert annual.ticket_count <= n
    # 一致性
    assert arch.total_investment == annual.total_investment
    mgr.clear()


@pytest.mark.parametrize("seed", range(30))
def test_flywheel_stability_matrix(seed, ticket_storage):
    """飞轮稳定性：多用户数据交错不串。"""
    rng = random.Random(1000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(1, 10)):
        lot = "dlt" if rng.random() < 0.5 else "ssq"
        draw = DRAW if lot == "dlt" else "2026-07-30"
        mgr.add(lot, JACKPOT_FRONT if lot == "dlt" else [4, 6, 10, 18, 23, 31],
                JACKPOT_BACK if lot == "dlt" else [11],
                buy_date="2026-07-31", draw_date=draw)
    tickets = [t.__dict__ for t in mgr.list_all()]

    dlt_tickets = [t for t in tickets if t["lottery"] == "dlt"]
    ssq_tickets = [t for t in tickets if t["lottery"] == "ssq"]
    rd = AutoReviewEngine.build(tickets, "dlt", DRAW)
    rs = AutoReviewEngine.build(tickets, "ssq", "2026-07-30")
    assert rd.ticket_count == len(dlt_tickets)
    assert rs.ticket_count == len(ssq_tickets)
    assert rd.total_winnings == len(dlt_tickets) * 5_000_000
    assert rs.total_winnings == len(ssq_tickets) * 5_000_000
    mgr.clear()


# ---------- 界面层集成（offscreen） ----------
@pytest.mark.parametrize("seed", range(3))
def test_dashboard_with_v42(seed, ticket_storage):
    """首页在 v4.2 数据下不崩，指标完整。"""
    from PySide6.QtWidgets import QApplication
    from windows.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    rng = random.Random(2000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(0, 6)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01")
    w = MainWindow()
    m = w.dashboard._value_metrics()
    assert len(m) == 6
    mgr.clear()
    w.deleteLater()


@pytest.mark.parametrize("seed", range(3))
def test_profile_page_v42(seed, ticket_storage):
    """个人中心在 v4.2 模块下不崩。"""
    from PySide6.QtWidgets import QApplication
    from windows.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    rng = random.Random(3000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(0, 5)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01")
    w = MainWindow()
    p = w.profile
    assert hasattr(p, "archive_area")
    assert hasattr(p, "premium_area")
    p._refresh()
    assert p.archive_area.text()
    assert p.premium_area.text()
    mgr.clear()
    w.deleteLater()


# ---------- 全链路端到端 ----------
def test_e2e_save_to_export(tmp_path, ticket_storage):
    """保存→档案→年度报告→PDF 导出。"""
    import os
    mgr = _seed_tickets(TicketManager(), n=3, win_first=True)
    tickets = [t.__dict__ for t in mgr.list_all()]
    annual = AnnualReportEngine.build(tickets, 2026)
    out = os.path.join(str(tmp_path), "annual.pdf")
    p = annual.export_pdf(out)
    assert os.path.exists(p)
    with open(p, "rb") as f:
        assert f.read(5) == b"%PDF-"
    mgr.clear()


@pytest.mark.parametrize("seed", range(15))
def test_e2e_random_export(seed, tmp_path, ticket_storage):
    """随机数据导出 PDF 稳定。"""
    import os
    rng = random.Random(4000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(1, 6)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01")
    tickets = [t.__dict__ for t in mgr.list_all()]
    annual = AnnualReportEngine.build(tickets, 2026)
    p = annual.export_pdf(os.path.join(str(tmp_path), f"a{seed}.pdf"))
    assert os.path.exists(p)
    mgr.clear()


def test_e2e_auto_review_notify(ticket_storage):
    """保存→自动复盘→通知文案。"""
    mgr = _seed_tickets(TicketManager(), n=2, win_first=True)
    tickets = [t.__dict__ for t in mgr.list_all()]
    reports = AutoReviewEngine.check_draws(tickets)
    assert len(reports) >= 1
    rep = reports[0]
    assert rep.participated
    assert "已开奖" in rep.notify_text()
    mgr.clear()
