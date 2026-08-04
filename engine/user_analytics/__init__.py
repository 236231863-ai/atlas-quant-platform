"""user_analytics - 用户事件分析系统（v4.6 P1）。

标准化事件（8类）+ 用户漏斗 + Retention Dashboard。
"""
from engine.user_analytics.analytics import (
    EVENT_NAMES,
    AnalyticsEvent,
    AnalyticsTracker,
    track,
)
from engine.user_analytics.funnel import (
    FunnelBuilder,
    FunnelReport,
    FunnelStage,
    build_funnel,
)
from engine.user_analytics.retention import (
    RetentionBuilder,
    RetentionMetrics,
    build_retention,
)

__all__ = [
    "EVENT_NAMES",
    "AnalyticsEvent",
    "AnalyticsTracker",
    "FunnelBuilder",
    "FunnelReport",
    "FunnelStage",
    "RetentionBuilder",
    "RetentionMetrics",
    "build_funnel",
    "build_retention",
    "track",
]
