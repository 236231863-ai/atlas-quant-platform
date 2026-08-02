"""assistant - 助手意图路由（AssistantIntentRouter）。

识别用户输入属于哪个业务任务（兑奖/热号/推荐/回测/报告/闲聊），
并给出是否需要更多信息。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .registry import register_tools, TOOL_KEYWORDS


@dataclass
class RouteResult:
    """路由结果。"""

    intent: str = "chat"          # 命中的意图（chat=闲聊）
    tool: str = ""                # 工具名
    confidence: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)
    is_business: bool = False     # 是否业务任务

    def to_dict(self) -> dict:
        return {
            "intent": self.intent, "tool": self.tool,
            "confidence": round(self.confidence, 2), "is_business": self.is_business,
        }


class AssistantIntentRouter:
    """助手意图路由器。"""

    def __init__(self):
        self.registry = register_tools()

    def route(self, query: str) -> RouteResult:
        """路由用户输入到业务工具或闲聊。"""
        if not query or not query.strip():
            return RouteResult()
        ql = query.lower()
        best_tool = ""
        best_hits = 0
        matched = []
        for tool in self.registry.all():
            hits = sum(1 for k in tool.keywords if k in ql)
            if hits > best_hits:
                best_hits = hits
                best_tool = tool.name
                matched = [k for k in tool.keywords if k in ql]
        if best_hits > 0:
            conf = 0.6 + 0.1 * best_hits
            return RouteResult(intent=best_tool, tool=best_tool, confidence=min(conf, 1.0),
                               matched_keywords=matched, is_business=True)
        return RouteResult()  # 闲聊

    def needs_more_info(self, query: str) -> str:
        """业务任务但缺信息时，给出引导。"""
        r = self.route(query)
        if not r.is_business:
            return ""
        if r.tool == "prize":
            from engine.lottery_intent import compute_prize_report
            rep = compute_prize_report(query)
            if rep.get("tickets", 0) == 0:
                return "请提供你的号码（例如：01 02 03 04 05 + 06 07），我帮你算中奖金额。"
        if r.tool in ("hot_cold", "recommend", "backtest", "report"):
            return ""
        return ""
