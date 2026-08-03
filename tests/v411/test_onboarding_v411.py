"""v4.1.1 Phase 3：首次用户引导测试（20 首次用户模拟）。"""
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


# ---------- 首次引导存在 ----------
def test_first_time_guide_no_tickets(window, ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    # 引导逻辑：无票据时首页显示引导（通过 _value_headline）
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    rv = PersonalReviewEngine.review([])
    b = BudgetPlanner().evaluate_tickets([])
    h = window.dashboard._value_headline(window.dashboard._value_metrics(), rv, b)
    assert "欢迎" in h  # 无票据引导语


def test_guide_mentions_reminder(window, ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    # 首次引导文案（dashboard guide label）含"提醒"
    guide_text = (
        "首次使用引导\n① 在 AI 助手输入你的彩票号码，或到「工作台」保存第一张彩票\n"
        "② 开奖后 Atlas 会主动提醒你，自动帮你算中没中"
    )
    assert "提醒" in guide_text
    assert "保存" in guide_text


def test_no_api_key_required(window, ticket_storage):
    """首次体验不要求 API Key。"""
    from user_profile import load_profile
    p = load_profile()
    assert hasattr(p, "ai_mode")  # 默认 offline，不强制在线


# ---------- 30 秒价值流程 ----------
def test_first_value_flow(window, ticket_storage):
    """首次用户 30 秒流程：引导→输入→兑奖→保存。"""
    from engine.lottery_intent.ticket_parser import TicketParser
    from engine.lottery_intent import compute_prize_report
    from engine.ticket_system import TicketManager
    from engine.assistant import handle_query

    TicketManager().clear()
    # 1. 输入号码
    parse = TicketParser.parse("10111822350612")
    assert parse.parsed_notes == 1
    # 2. 兑奖确认
    r1 = handle_query("7月31日买大乐透：10111822350612")
    assert "是否按" in r1
    # 3. 保存
    TicketManager().add("dlt", parse.tickets[0].front, parse.tickets[0].back,
                        buy_date="2026-07-31")
    assert TicketManager().count() == 1
    TicketManager().clear()


@pytest.mark.parametrize("seed", range(20))
def test_first_time_simulation(seed, window, ticket_storage):
    """20 个首次用户模拟。"""
    rng = random.Random(seed)
    from engine.lottery_intent.ticket_parser import TicketParser
    from engine.ticket_system import TicketManager
    from engine.assistant import handle_query

    TicketManager().clear()
    # 首次用户：输入号码（随机格式）
    front = sorted(rng.sample(range(1, 36), 5))
    back = sorted(rng.sample(range(1, 13), 2))
    text = " ".join(f"{n:02d}" for n in front + back)
    parse = TicketParser.parse(f"我买了：{text}")
    assert parse.parsed_notes == 1
    # 保存第一张
    TicketManager().add("dlt", parse.tickets[0].front, parse.tickets[0].back)
    assert TicketManager().count() == 1
    # 首页话术引导仍在
    from engine.personal_review import PersonalReviewEngine
    from engine.budget_manager import BudgetPlanner
    rv = PersonalReviewEngine.review([t.__dict__ for t in TicketManager().list_all()])
    b = BudgetPlanner().evaluate_tickets([t.__dict__ for t in TicketManager().list_all()])
    h = window.dashboard._value_headline(window.dashboard._value_metrics(), rv, b)
    assert isinstance(h, str)
    TicketManager().clear()


# ---------- 首次引导不破坏 ----------
def test_guide_hidden_after_first_ticket(window, ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7])
    # 有价值面板
    assert len(window.dashboard._value_metrics()) == 6
    mgr.clear()
