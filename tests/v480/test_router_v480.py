"""v4.8 P6：AI 助手融合测试。

覆盖：import_analyze / 亏损→资产 / 优先级。
"""
from __future__ import annotations

import pytest

from engine.assistant import registry


@pytest.fixture()
def seeded(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-08-01",
            draw_date="2026-08-01")
    return mgr


# ---------- 工具注册 ----------
def test_import_tool_registered():
    reg = registry.register_tools()
    assert "import_analyze" in reg.names()


def test_tool_count_9():
    assert len(registry.register_tools().names()) == 9


# ---------- 建档引导 ----------
def test_import_guide(ticket_storage):
    reg = registry.register_tools()
    r = reg.execute("import_analyze", "帮我建立彩票档案")
    assert "建立彩票档案" in r.text
    assert "4 种方式" in r.text


def test_import_numbers(ticket_storage):
    reg = registry.register_tools()
    r = reg.execute("import_analyze", "01 05 12 23 30 + 06 08")
    assert "导入完成" in r.text
    assert "成功导入：1" in r.text


def test_import_persists(ticket_storage):
    reg = registry.register_tools()
    reg.execute("import_analyze", "01 05 12 23 30 + 06 08")
    from engine.ticket_system import TicketManager
    assert TicketManager().count() == 1


# ---------- 亏损 → 资产 ----------
def test_loss_to_asset(seeded):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "我亏了多少")
    assert "我的彩票资产" in r.text


def test_behavior_no_tickets_guide(ticket_storage):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "分析我的彩票")
    assert "建立彩票档案" in r.text  # 引导建档


# ---------- 路由 ----------
def test_import_route(ticket_storage):
    from engine.assistant.router import AssistantIntentRouter
    r = AssistantIntentRouter().route("帮我建立彩票档案")
    assert r.tool == "import_analyze"


def test_prize_priority(seeded):
    from engine.assistant.router import AssistantIntentRouter
    r = AssistantIntentRouter().route("我中了多少钱")
    assert r.tool == "prize"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_import_stable(ticket_storage, i):
    reg = registry.register_tools()
    r = reg.execute("import_analyze", f"0{i} 05 12 23 30 + 06 08")
    assert r.text


@pytest.mark.parametrize("i", range(10))
def test_loss_stable(seeded, i):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "我亏了多少")
    assert r.text
