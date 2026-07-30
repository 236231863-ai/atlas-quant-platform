"""Human Review Workflow - human-in-the-loop research governance."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

class ReviewState(str, Enum):
    AI_PROPOSED = "ai_proposed"; HUMAN_REVIEW = "human_review"
    APPROVED = "approved"; REJECTED = "rejected"
    EXPERIMENT_RUNNING = "experiment_running"; COMPLETED = "completed"

@dataclass
class ReviewRecord:
    experiment_id: str; state: ReviewState = ReviewState.AI_PROPOSED
    reviewer: str = ""; comments: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self): return asdict(self)

class ResearchReviewSystem:
    def __init__(self): self._records: Dict[str, ReviewRecord] = {}
    def propose(self, exp_id: str) -> ReviewRecord:
        rec = ReviewRecord(experiment_id=exp_id, state=ReviewState.AI_PROPOSED)
        self._records[exp_id] = rec; return rec
    def get(self, exp_id: str) -> Optional[ReviewRecord]: return self._records.get(exp_id)
    def approve(self, exp_id: str, reviewer: str = "human") -> bool:
        rec = self.get(exp_id)
        if not rec or rec.state != ReviewState.AI_PROPOSED: return False
        rec.state = ReviewState.APPROVED; rec.reviewer = reviewer; rec.updated_at = datetime.now(timezone.utc).isoformat(); return True
    def reject(self, exp_id: str, reason: str, reviewer: str = "human") -> bool:
        rec = self.get(exp_id)
        if not rec: return False
        rec.state = ReviewState.REJECTED; rec.reviewer = reviewer; rec.comments.append(reason); rec.updated_at = datetime.now(timezone.utc).isoformat(); return True
    def comment(self, exp_id: str, comment: str) -> bool:
        rec = self.get(exp_id)
        if not rec: return False
        rec.comments.append(comment); return True
    def start_running(self, exp_id: str) -> bool:
        rec = self.get(exp_id)
        if not rec or rec.state != ReviewState.APPROVED: return False
        rec.state = ReviewState.EXPERIMENT_RUNNING; rec.updated_at = datetime.now(timezone.utc).isoformat(); return True
    def complete(self, exp_id: str) -> bool:
        rec = self.get(exp_id)
        if not rec: return False
        rec.state = ReviewState.COMPLETED; rec.updated_at = datetime.now(timezone.utc).isoformat(); return True
    def history(self) -> List[ReviewRecord]: return list(self._records.values())
    def list_by_state(self, state: ReviewState) -> List[ReviewRecord]:
        return [r for r in self._records.values() if r.state == state]
    def count(self) -> int: return len(self._records)
