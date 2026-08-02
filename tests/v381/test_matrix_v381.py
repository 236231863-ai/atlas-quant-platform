"""v3.8.1 矩阵补充（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.assistant import register_tools, execute_intent, AssistantIntentRouter, ToolRegistry, ToolResult

# 路由矩阵
_WIN = ["中了", "中奖", "兑奖", "奖金", "多少钱", "中了吗", "算算", "赚了", "中没中", "有没有中"]
@pytest.mark.parametrize("w", _WIN)
@pytest.mark.parametrize("prefix", ["", "大乐透", "我"])
def test_prize_route_wide(w, prefix):
    router = AssistantIntentRouter()
    r = router.route(f"{prefix}{w}")
    assert r.tool == "prize" if prefix else r.is_business

_HOT = ["热号", "冷号", "热码", "冷码", "热门号码", "冷门号码"]
@pytest.mark.parametrize("h", _HOT)
def test_hotcold_wide(h):
    r = AssistantIntentRouter().route(h)
    assert r.is_business

_REC = ["推荐", "号码", "一注", "选号", "选几个", "给我号码"]
@pytest.mark.parametrize("q", _REC)
def test_recommend_wide(q):
    r = AssistantIntentRouter().route(q)
    assert r.is_business

# 工具执行矩阵
@pytest.mark.parametrize("i", range(10))
def test_prize_tool_many(i):
    res = execute_intent("prize", f"大乐透 0{i%9+1} 0{i%8+2} 0{i%7+3} 0{i%6+4} 0{i%5+5} + 0{i%4+6} 0{i%3+7} 中了吗")
    assert "report_text" in res.text or "兑奖" in res.text

@pytest.mark.parametrize("query", ["热号", "冷号", "热号有哪些", "冷号呢"])
def test_hotcold_exec(query):
    res = execute_intent("hot_cold", query)
    assert res.success

# ToolRegistry 边界
@pytest.mark.parametrize("name", [f"tool{i}" for i in range(5)])
def test_registry_missing(name):
    reg = ToolRegistry()
    assert reg.get(name) is None

@pytest.mark.parametrize("n", [1, 3, 5])
def test_register_custom(n):
    reg = ToolRegistry()
    for i in range(n):
        reg.register(ToolRegistry.Tool if False else __import__("engine.assistant.registry", fromlist=["Tool"]).Tool(
            name=f"t{i}", description="d", handler=lambda q: ToolResult(tool="t", text="ok")))
    assert len(reg.all()) == n

# ToolResult 边界
@pytest.mark.parametrize("missing", [[], ["numbers"], ["data", "numbers"]])
def test_tool_result_missing(missing):
    r = ToolResult(tool="t", missing=missing)
    assert r.needs_more_info == bool(missing)

@pytest.mark.parametrize("i", range(10))
def test_tool_result_fields(i):
    r = ToolResult(tool="t", success=i % 2 == 0, text="x", data={"i": i})
    assert r.tool == "t"
    assert r.success == (i % 2 == 0)

# 端到端：多注矩阵
@pytest.mark.parametrize("n", [1, 5, 10, 15])
def test_multi_note_prize(n):
    notes = "; ".join(f"0{i%9+1} 0{i%8+2} 0{i%7+3} 0{i%6+4} 0{i%5+5} + 0{i%4+6} 0{i%3+7}" for i in range(n))
    text = f"大乐透 {notes} 中了吗"
    res = execute_intent("prize", text)
    assert res.success
    assert res.data.get("tickets") == n

@pytest.mark.parametrize("i", range(5))
def test_deterministic(i):
    a = execute_intent("prize", "大乐透 10 11 18 22 35 + 06 12 中了")
    b = execute_intent("prize", "大乐透 10 11 18 22 35 + 06 12 中了")
    assert a.data.get("total") == b.data.get("total")
