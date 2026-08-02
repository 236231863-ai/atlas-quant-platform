"""feedback - 反馈管理服务。

FeedbackManager：新增/查询/状态流转/统计 + 报告。
本地 JSON 存储（后续可接云）。
"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import asdict
from typing import Dict, List, Optional

from .models import (
    Feedback, BugReport, FeatureRequest, Rating,
    FEEDBACK_TYPES, STATUSES, SEVERITIES, PRIORITIES,
)


class FeedbackManager:
    """反馈管理器。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "feedback.json")
        self._items: Dict[str, Feedback] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                for fid, d in data.items():
                    t = d.get("type", "feedback")
                    cls = {"bug": BugReport, "feature": FeatureRequest, "rating": Rating}.get(t, Feedback)
                    # 构造：过滤合法字段
                    self._items[fid] = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, OSError, TypeError):
                self._items = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({fid: asdict(item) for fid, item in self._items.items()}, f, ensure_ascii=False, indent=2)

    # ---- 新增 ----
    def add(self, item: Feedback) -> Feedback:
        self._items[item.feedback_id] = item
        self._save()
        return item

    def add_feedback(self, content: str, user_id: str = "") -> Feedback:
        return self.add(Feedback(feedback_id=self._next_id("FB"), content=content, user_id=user_id))

    def add_bug(self, content: str, user_id: str = "", severity: str = "medium", steps: str = "") -> BugReport:
        return self.add(BugReport(
            feedback_id=self._next_id("BUG"), content=content, user_id=user_id,
            severity=severity if severity in SEVERITIES else "medium", steps=steps,
        ))

    def add_feature(self, content: str, user_id: str = "", priority: str = "medium", rationale: str = "") -> FeatureRequest:
        return self.add(FeatureRequest(
            feedback_id=self._next_id("FEAT"), content=content, user_id=user_id,
            priority=priority if priority in PRIORITIES else "medium", rationale=rationale,
        ))

    def add_rating(self, score: int, user_id: str = "", content: str = "") -> Optional[Rating]:
        if not 1 <= score <= 5:
            return None
        return self.add(Rating(feedback_id=self._next_id("RATE"), score=score, user_id=user_id, content=content))

    def _next_id(self, prefix: str) -> str:
        return f"{prefix}-{len(self._items) + 1:04d}"

    # ---- 查询 ----
    def get(self, feedback_id: str) -> Optional[Feedback]:
        return self._items.get(feedback_id)

    def list_all(self) -> List[Feedback]:
        return list(self._items.values())

    def by_status(self, status: str) -> List[Feedback]:
        return [f for f in self._items.values() if f.status == status]

    def by_type(self, ftype: str) -> List[Feedback]:
        return [f for f in self._items.values() if f.type == ftype]

    def count(self) -> int:
        return len(self._items)

    # ---- 状态 ----
    def transition(self, feedback_id: str, new_status: str) -> bool:
        f = self._items.get(feedback_id)
        if not f:
            return False
        ok = f.transition(new_status)
        if ok:
            self._save()
        return ok

    # ---- 报告 ----
    def report(self) -> dict:
        items = self.list_all()
        status_counter = Counter(f.status for f in items)
        type_counter = Counter(f.type for f in items)
        severities = Counter(getattr(f, "severity", "") for f in items if f.type == "bug")
        scores = [getattr(f, "score", 0) for f in items if f.type == "rating"]
        avg_rating = round(sum(scores) / len(scores), 2) if scores else 0.0
        return {
            "total": len(items),
            "by_status": dict(status_counter),
            "by_type": dict(type_counter),
            "bug_severities": dict(severities),
            "avg_rating": avg_rating,
            "rating_count": len(scores),
            "open_count": len([f for f in items if f.status in ("new", "reviewing")]),
            "closed_count": len([f for f in items if f.status == "closed"]),
        }

    def clear(self) -> None:
        self._items = {}
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
