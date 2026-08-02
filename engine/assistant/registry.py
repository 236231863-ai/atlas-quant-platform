"""assistant - 工具注册表（Tool Registry）。

注册所有业务工具（复用已有能力），供 Intent Router 调用。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class ToolResult:
    """工具执行结果。"""

    tool: str
    success: bool = True
    text: str = ""
    data: dict = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)  # 缺失信息

    @property
    def needs_more_info(self) -> bool:
        return bool(self.missing)


@dataclass
class Tool:
    """工具定义。"""

    name: str
    description: str
    handler: Callable[[str], ToolResult]
    keywords: List[str] = field(default_factory=list)  # 触发关键词


class ToolRegistry:
    """工具注册表。"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def all(self) -> List[Tool]:
        return list(self._tools.values())

    def names(self) -> List[str]:
        return list(self._tools.keys())

    def execute(self, name: str, query: str) -> ToolResult:
        t = self._tools.get(name)
        if not t:
            return ToolResult(tool=name, success=False, text=f"未知工具：{name}")
        try:
            return t.handler(query)
        except Exception as e:
            return ToolResult(tool=name, success=False, text=f"工具执行失败：{e}")


# ---------------- 工具处理器 ----------------
def _prize_handler(query: str) -> ToolResult:
    """兑奖计算工具。"""
    from engine.lottery_intent import compute_prize_report
    r = compute_prize_report(query)
    if not r.get("is_prize"):
        return ToolResult(tool="prize", text=r.get("report_text", "未识别到兑奖意图。"))
    if r.get("tickets", 0) == 0:
        return ToolResult(
            tool="prize", success=False,
            text="未解析到有效号码。请提供号码，例如：01 02 03 04 05 + 06 07。",
            missing=["numbers"],
        )
    return ToolResult(tool="prize", text=r["report_text"], data={
        "lottery": r.get("lottery"), "tickets": r.get("tickets"),
        "won": r.get("won_notes"), "total": r.get("total"),
    })


def _hot_numbers_handler(query: str) -> ToolResult:
    from data_loader import load_draws
    from stats import hot_numbers, cold_numbers
    draws = load_draws()
    if not draws:
        return ToolResult(tool="hot_cold", success=False, text="暂无数据。", missing=["data"])
    if "冷" in query:
        cold = cold_numbers(draws, 8)
        return ToolResult(tool="hot_cold", text="近期冷号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in cold))
    hot = hot_numbers(draws, 8)
    return ToolResult(tool="hot_cold", text="近期热号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in hot))


def _recommend_handler(query: str) -> ToolResult:
    from data_loader import load_draws
    from stats import recommendation
    draws = load_draws()
    if not draws:
        return ToolResult(tool="recommend", success=False, text="暂无数据。", missing=["data"])
    method = "cold" if "冷" in query else "balanced" if "均衡" in query else "hot"
    rec = recommendation(draws, method)
    label = {"hot": "热号", "cold": "冷号", "balanced": "奇偶均衡"}[method]
    return ToolResult(tool="recommend", text=f"{label}推荐：{' '.join(f'{n:02d}' for n in rec['front'])} + {' '.join(f'{n:02d}' for n in rec['back'])}")


def _backtest_handler(query: str) -> ToolResult:
    return ToolResult(tool="backtest", text="回测工具：请在「回测中心」页面选择策略运行，这里仅提示。")


def _report_handler(query: str) -> ToolResult:
    return ToolResult(tool="report", text="报告工具：请到「研究报告」页面一键生成并导出。")


# 能力地图：工具 → 触发关键词
TOOL_KEYWORDS = {
    "prize": ["中了", "中奖", "兑奖", "奖金", "多少钱", "中了吗", "算算", "赚了", "中没中", "有没有中", "中了没"],
    "hot_cold": ["热号", "冷号", "热码", "冷码"],
    "recommend": ["推荐", "号码", "一注", "选号", "选几个", "选一些"],
    "backtest": ["回测", "验证策略", "策略表现"],
    "report": ["报告", "生成报告", "分析报告"],
}


def register_tools() -> ToolRegistry:
    """注册全部业务工具。"""
    reg = ToolRegistry()
    reg.register(Tool(name="prize", description="兑奖计算", handler=_prize_handler, keywords=TOOL_KEYWORDS["prize"]))
    reg.register(Tool(name="hot_cold", description="热号/冷号查询", handler=_hot_numbers_handler, keywords=TOOL_KEYWORDS["hot_cold"]))
    reg.register(Tool(name="recommend", description="号码推荐", handler=_recommend_handler, keywords=TOOL_KEYWORDS["recommend"]))
    reg.register(Tool(name="backtest", description="回测指引", handler=_backtest_handler, keywords=TOOL_KEYWORDS["backtest"]))
    reg.register(Tool(name="report", description="报告指引", handler=_report_handler, keywords=TOOL_KEYWORDS["report"]))
    return reg


def execute_intent(intent: str, query: str, registry: Optional[ToolRegistry] = None) -> ToolResult:
    """按意图执行工具。"""
    reg = registry or register_tools()
    if intent in reg.names():
        return reg.execute(intent, query)
    return ToolResult(tool=intent, success=False, text=f"未知意图：{intent}")
