"""user_events - 用户行为事件追踪（v4.3 验收基础设施 + v4.5 P5 行为报告）。"""
from engine.user_events.events import (
    EVENT_TYPES,
    EventTracker,
    UserEvent,
    record_event,
)
from engine.user_events.report import (
    BehaviorReporter,
    BehaviorSummary,
    UserBehaviorReport,
    build_behavior_report,
)

__all__ = [
    "EVENT_TYPES",
    "BehaviorReporter",
    "BehaviorSummary",
    "EventTracker",
    "UserBehaviorReport",
    "UserEvent",
    "build_behavior_report",
    "record_event",
]
