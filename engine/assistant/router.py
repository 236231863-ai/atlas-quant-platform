"""assistant - 助手意图路由（AssistantIntentRouter，v3.8.2-P1）。

识别用户输入属于哪个业务任务（兑奖/热号/推荐/回测/报告/闲聊），
并给出是否需要更多信息。

v3.8.2-P1 修复（Phase 4）——确认回复优先级：
  1. PendingTask 确认（用户回复 是/好的/确认/按这个算 → 恢复上一任务）
  2. 业务工具（兑奖/热号/推荐/回测/报告）
  3. 普通 LLM（闲聊兜底）
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .registry import register_tools, TOOL_KEYWORDS


@dataclass
class RouteResult:
    """路由结果。"""

    intent: str = "chat"          # 命中的意图（chat=闲聊；prize=兑奖…）
    tool: str = ""                # 工具名
    confidence: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)
    is_business: bool = False     # 是否业务任务
    is_confirm: bool = False      # 是否确认回复（v3.8.2-P1：恢复 PendingTask）
    is_deny: bool = False         # 是否否定回复（取消任务）
    pending_task: Optional["object"] = None   # 待确认任务

    def to_dict(self) -> dict:
        return {
            "intent": self.intent, "tool": self.tool,
            "confidence": round(self.confidence, 2), "is_business": self.is_business,
            "is_confirm": self.is_confirm, "is_deny": self.is_deny,
        }


class AssistantIntentRouter:
    """助手意图路由器（v3.8.2-P1：确认回复优先）。"""

    def __init__(self, user_id: str = "default"):
        self.registry = register_tools()
        self.user_id = user_id

    # ---------- 优先级 1：PendingTask 确认 ----------
    def _check_confirm(self, query: str):
        """检查用户回复是否为确认/否定，并携带待确认任务。

        无任务但用户确认/否定时仍返回标记，让调用方给出友好提示
        （避免确认回复落回普通聊天 → 状态丢失）。
        """
        from engine.task_context import PendingTaskManager
        mgr = PendingTaskManager()
        task = mgr.get_pending_task(self.user_id)
        is_confirm = PendingTaskManager.is_confirm_reply(query)
        is_deny = PendingTaskManager.is_deny_reply(query)
        if not is_confirm and not is_deny:
            return None
        if task is None:
            if is_confirm:
                return RouteResult(intent="confirm", tool="prize", confidence=0.9,
                                   is_business=True, matched_keywords=["确认回复"],
                                   is_confirm=True, pending_task=None)
            return RouteResult(intent="chat", tool="", confidence=0.8,
                               is_business=False, is_deny=True, pending_task=None)
        if is_confirm:
            return RouteResult(intent="confirm", tool=task.task_type,
                               confidence=1.0, is_business=True,
                               matched_keywords=["确认回复"], is_confirm=True,
                               pending_task=task)
        return RouteResult(intent="chat", tool="", confidence=0.8,
                           is_business=False, is_deny=True, pending_task=task)

    def route(self, query: str, user_id: Optional[str] = None) -> RouteResult:
        """路由用户输入到业务工具或闲聊（确认回复优先级最高）。"""
        if user_id is not None:
            self.user_id = user_id
        if not query or not query.strip():
            return RouteResult()

        # 优先级 1：确认/否定 → 恢复或取消 PendingTask
        confirm = self._check_confirm(query)
        if confirm is not None:
            return confirm

        # 优先级 2：业务工具（quant 强意图词加权）
        from .registry import QUANT_STRONG_WORDS
        ql = query.lower()
        best_tool = ""
        best_hits = 0
        matched = []
        for tool in self.registry.all():
            hits = sum(1 for k in tool.keywords if k in ql)
            if tool.name == "quant_analyze":
                hits += sum(1 for k in QUANT_STRONG_WORDS if k in ql)
            if hits > best_hits:
                best_hits = hits
                best_tool = tool.name
                matched = [k for k in tool.keywords if k in ql]
        if best_hits > 0:
            conf = 0.6 + 0.1 * best_hits
            return RouteResult(intent=best_tool, tool=best_tool, confidence=min(conf, 1.0),
                               matched_keywords=matched, is_business=True)

        # 兜底：有号码 + 购彩语义（买/注/组/票/兑）→ 兑奖（v3.8.2-P1）
        if re.search(r"\d{1,2}", ql) and any(k in ql for k in ("买", "购", "兑", "注", "组", "票")):
            from engine.lottery_intent.intent_router import LotteryIntentRouter
            det = LotteryIntentRouter.detect(query)
            if det.is_prize_intent:
                return RouteResult(intent="prize", tool="prize", confidence=0.7,
                                   is_business=True, matched_keywords=["兑奖语义"])

        # 优先级 3：普通聊天
        return RouteResult()

    def needs_more_info(self, query: str) -> str:
        """业务任务但缺信息时，给出引导。"""
        r = self.route(query)
        if r.is_confirm:
            return ""  # 确认由调用方恢复任务
        if not r.is_business:
            return ""
        if r.tool == "prize":
            from engine.lottery_intent import compute_prize_report
            rep = compute_prize_report(query, user_id=self.user_id)
            if rep.get("tickets", 0) == 0:
                return "请提供你的号码（例如：01 02 03 04 05 + 06 07，或连续号码串 13212326330112），我帮你算中奖金额。"
        if r.tool in ("hot_cold", "recommend", "backtest", "report"):
            return ""
        return ""
