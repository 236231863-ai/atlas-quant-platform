"""feedback - 用户反馈中心（v3.7.1 Phase 3）。

Feedback / BugReport / FeatureRequest / Rating + 状态机（New/Reviewing/Fixed/Closed）。
"""
from .models import (
    Feedback, BugReport, FeatureRequest, Rating,
    FEEDBACK_TYPES, STATUSES, SEVERITIES, PRIORITIES,
)
from .service import FeedbackManager

__all__ = [
    "Feedback", "BugReport", "FeatureRequest", "Rating",
    "FeedbackManager", "FEEDBACK_TYPES", "STATUSES", "SEVERITIES", "PRIORITIES",
]
