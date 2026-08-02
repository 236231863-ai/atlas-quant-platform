"""v3.8.1 测试：AI 助手工具路由（Tool Registry + AssistantIntentRouter + 端到端）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.assistant import (
    ToolRegistry, ToolResult, register_tools, execute_intent,
    AssistantIntentRouter, RouteResult,
)

@pytest.fixture
def registry():
    return register_tools()

@pytest.fixture
def router():
    return AssistantIntentRouter()

# ---------- 工具注册 ----------
@pytest.mark.parametrize("name", ["prize", "hot_cold", "recommend", "backtest", "report"])
def test_tools_registered(registry, name):
    assert registry.get(name) is not None

@pytest.mark.parametrize("name", ["bad", "unknown"])
def test_tools_missing(registry, name):
    assert registry.get(name) is None

@pytest.mark.parametrize("name", ["prize", "hot_cold", "recommend", "backtest", "report"])
def test_tool_descriptions(registry, name):
    t = registry.get(name)
    assert t.description and t.keywords

@pytest.mark.parametrize("n", [1, 3, 5])
def test_tool_count(registry, n):
    assert len(registry.all()) == 5
    assert len(registry.names()) == 5

# ---------- 路由 ----------
@pytest.mark.parametrize("query,expected", [
    ("我中了多少钱", "prize"),
    ("帮我算算中奖", "prize"),
    ("热号有哪些", "hot_cold"),
    ("冷号有哪些", "hot_cold"),
    ("推荐一注号码", "recommend"),
    ("选几个号", "recommend"),
    ("帮我生成报告", "report"),
    ("回测一下", "backtest"),
])
def test_route_business(router, query, expected):
    r = router.route(query)
    assert r.tool == expected
    assert r.is_business

@pytest.mark.parametrize("query", ["你好", "谢谢", "天气怎么样", "你是谁", ""])
def test_route_chat(router, query):
    r = router.route(query)
    assert not r.is_business

@pytest.mark.parametrize("i", range(10))
def test_route_confidence(router, i):
    r = router.route("中了多少钱")
    assert r.confidence > 0

@pytest.mark.parametrize("query", ["中了", "中奖了吗"])
def test_route_prize(router, query):
    r = router.route(query)
    assert r.is_business

# ---------- 工具执行 ----------
def test_execute_prize():
    res = execute_intent("prize", "大乐透 10 11 18 22 35 + 06 12 中了吗")
    assert res.success
    assert "兑奖" in res.text

@pytest.mark.parametrize("query", ["热号", "冷号"])
def test_execute_hot_cold(query):
    res = execute_intent("hot_cold", query)
    assert res.success
    assert "号" in res.text

def test_execute_recommend():
    res = execute_intent("recommend", "推荐号码")
    assert res.success

def test_execute_unknown():
    res = execute_intent("bad_tool", "x")
    assert not res.success

# ---------- 缺失信息引导 ----------
@pytest.mark.parametrize("query", ["我中了多少钱", "帮我算奖金"])
def test_needs_more_info(router, query):
    guide = router.needs_more_info(query)
    assert "号码" in guide

@pytest.mark.parametrize("query", ["热号有哪些"])
def test_no_guide_needed(router, query):
    assert router.needs_more_info(query) == ""

# ---------- 端到端（验收场景） ----------
def test_acceptance_scenario(router):
    text = ("7月31日买了这些号码：01 02 03 04 05 + 06 07；10 11 18 22 35 + 06 12；"
            "15 20 25 30 33 + 03 09；08 12 15 19 26 + 02 11；01 05 10 20 30 + 07 12；"
            "11 22 33 34 35 + 05 09；04 09 14 19 24 + 01 08；02 07 12 17 22 + 04 10；"
            "06 11 16 21 26 + 02 07；10 12 18 22 35 + 06 12；13 18 23 28 33 + 05 10；"
            "03 08 13 18 23 + 01 06；16 21 26 31 35 + 07 12；05 10 15 20 25 + 06 08；"
            "19 24 29 34 35 + 09 11。8月1日开奖，我中了多少钱？")
    r = router.route(text)
    assert r.tool == "prize"
    res = execute_intent("prize", text)
    assert res.success
    assert res.data.get("tickets") == 15

@pytest.mark.parametrize("i", range(5))
def test_acceptance_deterministic(router, i):
    text = "大乐透 10 11 18 22 35 + 06 12 中了"
    res1 = execute_intent("prize", text)
    res2 = execute_intent("prize", text)
    assert res1.data.get("total") == res2.data.get("total")
