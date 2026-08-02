"""task_context - Pending Task 上下文系统（v3.8.2-P1 Phase 1）。

解决兑奖任务链路状态丢失：
  用户问兑奖 → Atlas 返回确认（是否按下一开奖计算）→ 用户确认
  → 自动恢复上一任务并完成兑奖。

核心：PendingTaskManager（持久化，重启可恢复）。
"""
from .manager import PendingTask, PendingTaskManager

__all__ = ["PendingTask", "PendingTaskManager"]
