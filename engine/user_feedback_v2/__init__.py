"""user_feedback_v2 - 用户反馈智能（v3.7.0 Phase 4）。

UserFeedbackTracker：本地行为事件追踪（页面/功能/导出/策略/偏好）。
UserBehaviorReport：行为汇总报告。
"""
from .tracker import UserFeedbackTracker, EVENT_TYPES
from .report import UserBehaviorReport, build_behavior_report

__all__ = ["UserFeedbackTracker", "UserBehaviorReport", "build_behavior_report", "EVENT_TYPES"]
