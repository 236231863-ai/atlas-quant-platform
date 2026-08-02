"""feedback - 反馈模型。

Feedback 基类 + BugReport / FeatureRequest / Rating。
状态：New / Reviewing / Fixed / Closed。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

FEEDBACK_TYPES = {"feedback", "bug", "feature", "rating"}
STATUSES = {"new", "reviewing", "fixed", "closed"}
SEVERITIES = {"low", "medium", "high", "critical"}
PRIORITIES = {"low", "medium", "high"}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Feedback:
    """通用反馈基类。"""

    feedback_id: str
    type: str = "feedback"
    user_id: str = ""
    content: str = ""
    status: str = "new"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def transition(self, new_status: str) -> bool:
        if new_status not in STATUSES:
            return False
        self.status = new_status
        self.updated_at = _now()
        return True


@dataclass
class BugReport(Feedback):
    """Bug 报告。"""

    type: str = "bug"
    severity: str = "medium"
    steps: str = ""


@dataclass
class FeatureRequest(Feedback):
    """功能请求。"""

    type: str = "feature"
    priority: str = "medium"
    rationale: str = ""


@dataclass
class Rating(Feedback):
    """评分。"""

    type: str = "rating"
    score: int = 5  # 1-5

    def __post_init__(self):
        if not 1 <= self.score <= 5:
            raise ValueError("score must be 1-5")
