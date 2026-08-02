"""user_intelligence/v3 - 用户行为智能（v3.8.0 Phase 1）。

标准事件：APP_START / ANALYSIS_RUN / REPORT_EXPORT / BACKTEST_RUN / STRATEGY_SAVE / FEEDBACK_SEND
提供用户行为统计与用户画像标签。
"""
from .events import UserIntelligenceV3, BehaviorSummary, build_behavior_summary, EVENTS

__all__ = ["UserIntelligenceV3", "BehaviorSummary", "build_behavior_summary", "EVENTS"]
