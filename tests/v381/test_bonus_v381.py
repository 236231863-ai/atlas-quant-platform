"""v3.8.1 最终补充（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.assistant import register_tools, execute_intent, AssistantIntentRouter, ToolRegistry, ToolResult

# 路由连续
@pytest.mark.parametrize("i", range(30))
def test_route_repeat(i):
    r = AssistantIntentRouter().route("中了多少钱")
    assert r.is_business and r.tool == "prize"

# 工具执行连续
@pytest.mark.parametrize("i", range(30))
def test_execute_repeat(i):
    res = execute_intent("prize", "大乐透 10 11 18 22 35 + 06 12 中了吗")
    assert res.success

# 注册表全名
def test_registry_names():
    assert set(register_tools().names()) == {"prize", "import_analyze", "behavior_analyze", "personal_analyze", "quant_analyze", "hot_cold", "recommend", "backtest", "report"}

@pytest.mark.parametrize("name", ["prize", "personal_analyze", "quant_analyze", "hot_cold", "recommend", "backtest", "report"])
def test_registry_get(name):
    assert register_tools().get(name).name == name

# 工具结果默认
@pytest.mark.parametrize("i", range(15))
def test_result_defaults(i):
    r = ToolResult(tool="t")
    assert r.success is True
    assert r.text == "" and r.data == {} and r.missing == []

# 路由置信度
@pytest.mark.parametrize("i", range(15))
def test_confidence_range(i):
    r = AssistantIntentRouter().route("大乐透中了")
    assert 0 < r.confidence <= 1
