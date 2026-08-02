"""assistant - AI 助手工具路由层（v3.8.1）。

让 AI 助手成为任务执行助手，而不是普通聊天机器人：
  - Tool Registry    : 注册已有业务工具
  - AssistantIntentRouter : 识别任务类型 → 路由到对应工具
  - 缺失信息引导      : 参数不足时给出下一步提示
"""
from .registry import ToolRegistry, ToolResult, register_tools, execute_intent
from .router import AssistantIntentRouter, RouteResult

__all__ = ["ToolRegistry", "ToolResult", "register_tools", "execute_intent", "AssistantIntentRouter", "RouteResult"]
