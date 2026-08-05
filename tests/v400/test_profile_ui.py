"""v4.0.0 Phase 6：个人中心页面 UI 测试。"""
from __future__ import annotations

import os

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
def ticket_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("engine.ticket_system.manager.os.path.expanduser",
                        lambda *a, **k: str(tmp_path))
    return str(tmp_path)


# ---------- 导航 ----------
def test_pages_include_profile(window):
    assert "个人中心" in window.nav._pages


def test_stack_count_9(window):
    assert window.stack.count() == 9


def test_profile_page_exists(window):
    assert hasattr(window, "profile")


def test_switch_to_profile(window):
    window.switch_page("个人中心")
    assert window.stack.currentWidget() is window.profile


def test_nav_all_pages(window):
    assert len(window.nav._pages) == 9


# ---------- 页面结构 ----------
def test_profile_cards(window):
    p = window.profile
    for card in (p.ticket_card, p.spend_card, p.win_card, p.risk_card):
        assert card.value_label is not None


def test_profile_disclaimer(window):
    assert "随机性" in window.profile.disclaimer.text()


def test_report_area(window):
    assert isinstance(window.profile.report_area.text(), str)


def test_trend_area(window):
    assert isinstance(window.profile.trend_area.text(), str)


# ---------- 空数据 ----------
def test_empty_state(window, ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    window.profile._refresh()
    p = window.profile
    assert p.ticket_card.value_label.text() == "0"
    assert "暂无" in p.report_area.text() or "0" in p.ticket_card.value_label.text()


# ---------- 有数据 ----------
def test_profile_with_tickets(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12], buy_date="2026-07-31",
            draw_date="2026-08-01")
    window.profile._refresh()
    assert window.profile.ticket_card.value_label.text() == "2"
    assert "¥" in window.profile.spend_card.value_label.text()
    mgr.clear()


def test_profile_win_card(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12], buy_date="2026-07-31",
            draw_date="2026-08-01")
    window.profile._refresh()
    assert "5,000,000" in window.profile.win_card.value_label.text()
    mgr.clear()


def test_profile_risk_card(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    for i in range(10):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date=f"2026-07-{i + 1:02d}")
    window.profile._refresh()
    assert window.profile.risk_card.value_label.text() in ("A", "B", "C", "D")
    mgr.clear()


# ---------- 报告/趋势内容 ----------
def test_report_content(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    window.profile._refresh()
    assert "复盘报告" in window.profile.report_area.text()
    mgr.clear()


def test_trend_content(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    window.profile._refresh()
    assert "月度投入趋势" in window.profile.trend_area.text()
    mgr.clear()


@pytest.mark.parametrize("n", [1, 3, 5, 8])
def test_ticket_count_refresh(window, ticket_storage, n):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(n):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date=f"2026-07-{i + 1:02d}")
    window.profile._refresh()
    assert window.profile.ticket_card.value_label.text() == str(n)
    mgr.clear()


# ---------- 预算健康 ----------
def test_budget_in_report(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    window.profile._refresh()
    assert "预算健康度" in window.profile.report_area.text() or "暂无" in window.profile.report_area.text()
    mgr.clear()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_profile_matrix(seed, window, ticket_storage):
    import random
    rng = random.Random(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 10)):
        mgr.add("dlt", sorted(rng.sample(range(1, 36), 5)),
                sorted(rng.sample(range(1, 13), 2)),
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    window.profile._refresh()
    assert window.profile.ticket_card.value_label.text() == str(mgr.count())
    assert window.profile.risk_card.value_label.text() in ("A", "B", "C", "D")
    mgr.clear()


@pytest.mark.parametrize("seed", range(30))
def test_profile_no_crash(seed, window, ticket_storage):
    import random
    rng = random.Random(1000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 6)):
        mgr.add("dlt", sorted(rng.sample(range(1, 36), 5)),
                sorted(rng.sample(range(1, 13), 2)),
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    window.profile._refresh()
    assert isinstance(window.profile.report_area.text(), str)
    mgr.clear()


@pytest.mark.parametrize("seed", range(30))
def test_profile_win_refresh(seed, window, ticket_storage):
    import random
    rng = random.Random(2000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 5)):
        mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12],
                buy_date="2026-07-31", draw_date="2026-08-01")
    window.profile._refresh()
    assert "¥" in window.profile.win_card.value_label.text()
    mgr.clear()
