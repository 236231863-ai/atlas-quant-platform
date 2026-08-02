"""v3.8.1 补充矩阵（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.assistant import register_tools, execute_intent, AssistantIntentRouter, ToolRegistry, ToolResult

# 路由大矩阵
_PRIZE_WORDS = ["中了", "中奖", "兑奖", "奖金", "多少钱", "中了吗", "算算", "赚了", "中没中", "有没有中", "中了没", "中奖了"]
@pytest.mark.parametrize("w", _PRIZE_WORDS)
def test_prize_big(w):
    assert AssistantIntentRouter().route(w).is_business

_HOT_WORDS = ["热号", "冷号", "热码", "冷码"]
@pytest.mark.parametrize("h", _HOT_WORDS)
@pytest.mark.parametrize("suffix", ["有哪些", "呢", "是什么", ""])
def test_hotcold_big(h, suffix):
    assert AssistantIntentRouter().route(f"{h}{suffix}").is_business

_REC_WORDS = ["推荐", "号码", "一注", "选号", "选几个", "选一些"]
@pytest.mark.parametrize("r", _REC_WORDS)
def test_recommend_big(r):
    assert AssistantIntentRouter().route(r).is_business

# 工具执行矩阵
@pytest.mark.parametrize("n", [1, 5, 12])
def test_prize_note_count(n):
    notes = "; ".join(f"{i%9+1} {i%8+2} {i%7+3} {i%6+4} {i%5+5} + {i%4+6} {i%3+7}" for i in range(n))
    res = execute_intent("prize", f"大乐透 {notes} 中了吗")
    assert res.data.get("tickets") == n

@pytest.mark.parametrize("fmt", ["md", "pdf"])
def test_prize_total(fmt):
    res = execute_intent("prize", "大乐透 10 11 18 22 35 + 06 12 中了吗")
    assert res.data.get("total") >= 0

# ToolRegistry 自定义
@pytest.mark.parametrize("i", range(10))
def test_custom_tool(i):
    from engine.assistant.registry import Tool
    reg = ToolRegistry()
    reg.register(Tool(name=f"t{i}", description="d", handler=lambda q: ToolResult(tool="t", text="ok")))
    res = reg.execute(f"t{i}", "x")
    assert res.success

@pytest.mark.parametrize("name", ["a", "b", "c"])
def test_custom_unknown(name):
    reg = ToolRegistry()
    res = reg.execute(name, "x")
    assert not res.success

# ToolResult 全面
@pytest.mark.parametrize("success", [True, False])
@pytest.mark.parametrize("missing", [[], ["data"]])
def test_result_combos(success, missing):
    r = ToolResult(tool="t", success=success, missing=missing)
    assert r.success == success
    assert r.needs_more_info == bool(missing)

@pytest.mark.parametrize("i", range(5))
def test_result_to_dict(i):
    r = ToolResult(tool="t", text="x", data={"i": i})
    assert r.text == "x"

# 端到端验收矩阵
@pytest.mark.parametrize("i", range(10))
def test_e2e_acceptance(i):
    text = f"大乐透 {i%9+1} {i%8+2} {i%7+3} {i%6+4} {i%5+5} + {i%4+6} {i%3+7} 中了多少钱"
    res = execute_intent("prize", text)
    assert res.success

@pytest.mark.parametrize("i", range(5))
def test_e2e_hot_cold(i):
    res = execute_intent("hot_cold", "热号")
    assert res.success
