"""assistant - AI 助手工具路由层（v3.8.2-P1 确认恢复）。

让 AI 助手成为任务执行助手，而不是普通聊天机器人：
  - Tool Registry            : 注册已有业务工具
  - AssistantIntentRouter    : 识别任务类型 → 路由到对应工具
  - PendingTask 确认恢复     : 用户回复"是/好的/确认/按这个算" → 恢复上一任务
  - handle_query             : 统一入口（确认→恢复；业务→工具；否则→LLM）
"""
from .registry import ToolRegistry, ToolResult, register_tools, execute_intent
from .router import AssistantIntentRouter, RouteResult

__all__ = [
    "ToolRegistry", "ToolResult", "register_tools", "execute_intent",
    "AssistantIntentRouter", "RouteResult", "handle_query",
]


def handle_query(query: str, user_id: str = "default") -> str:
    """统一处理用户消息，返回助手回复文本。

    优先级（v3.8.2-P1）：
      1. PendingTask 确认   → confirm_prize_task 恢复并计算
      2. 否定回复          → cancel_prize_task 清除任务
      3. 业务工具          → execute_intent（兑奖/热号/推荐/回测/报告）
      4. 普通聊天          → 返回 ""（由调用方走 LLM/规则）

    注意：确认/否定分支会消费 PendingTask（一次性）。
    """
    router = AssistantIntentRouter(user_id)
    route = router.route(query, user_id=user_id)

    # 1) 确认回复 → 恢复 PendingTask 完成兑奖
    if route.is_confirm:
        from engine.lottery_intent import confirm_prize_task
        r = confirm_prize_task(user_id)
        return r.get("report_text", "✅ 已恢复兑奖任务。")

    # 2) 否定回复 → 清除任务
    if route.is_deny:
        from engine.lottery_intent import cancel_prize_task
        r = cancel_prize_task(user_id)
        return r.get("report_text", "已取消本次兑奖计算。")

    # 3) 业务工具
    if route.is_business:
        guide = router.needs_more_info(query)
        if guide:
            return guide
        res = execute_intent(route.tool, query, user_id=user_id)
        if res.text:
            # 成功返回结果；失败时返回引导文案（如"暂无投注数据"）
            return res.text

    # 4) 普通聊天 → 调用方处理
    return ""
