"""v4.7 P5：AI 助手融合测试。

覆盖：behavior_analyze 工具 / 关键词路由 / 优先级。
"""
from __future__ import annotations

import pytest

from engine.assistant import registry


@pytest.fixture()
def seeded(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [1, 2], buy_date="2026-07-31",
            draw_date="2026-08-01")
    mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12], buy_date="2026-08-01",
            draw_date="2026-08-01")
    return mgr


# ---------- 工具注册 ----------
def test_tool_registered():
    reg = registry.register_tools()
    assert "behavior_analyze" in reg.names()


def test_tool_order_after_prize():
    """优先级：兑奖 > 行为分析 > 个人分析。"""
    reg = registry.register_tools()
    names = reg.names()
    assert names.index("prize") < names.index("behavior_analyze") < names.index("personal_analyze")


# ---------- 行为分析 ----------
def test_behavior_handler(seeded):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "分析我今年买彩票情况")
    assert "投注画像" in r.text


def test_behavior_score_handler(seeded):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "我的购彩习惯怎么样")
    assert "健康分" in r.text


def test_behavior_no_tickets(ticket_storage):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "分析我买彩票情况")
    assert r.success is False


# ---------- 关键词路由 ----------
@pytest.mark.parametrize("q", ["分析我今年买彩票情况", "我的中奖率怎么样",
                               "我的购彩风险等级是多少", "我过去的方法有没有效果"])
def test_keywords_behavior(q, seeded):
    from engine.assistant.router import AssistantIntentRouter
    r = AssistantIntentRouter().route(q)
    assert r.tool == "behavior_analyze"


@pytest.mark.parametrize("q", ["我的购彩习惯", "健康分是多少", "我是不是亏很多"])
def test_keywords_score(q, seeded):
    from engine.assistant.router import AssistantIntentRouter
    r = AssistantIntentRouter().route(q)
    assert r.tool == "behavior_analyze"


# ---------- 兑奖优先 ----------
def test_prize_priority(seeded):
    from engine.assistant.router import AssistantIntentRouter
    r = AssistantIntentRouter().route("我中了多少钱")
    assert r.tool == "prize"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_behavior_repeat(seeded, i):
    reg = registry.register_tools()
    r = reg.execute("behavior_analyze", "分析我买彩票情况")
    assert r.text
