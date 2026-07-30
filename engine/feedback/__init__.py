"""Feedback Intelligence - collect and analyze execution results."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class FeedbackInsight: insight_id:str; prediction:str; action:str; actual_result:str; error:float=0.0; success_factors:List[str]=field(default_factory=list); failure_reasons:List[str]=field(default_factory=list); def to_dict(self):return asdict(self)

class FeedbackIntelligence:
    def __init__(self): self._insights: Dict[str, FeedbackInsight] = {}
    def record(self, insight: FeedbackInsight): self._insights[insight.insight_id] = insight; return insight
    def analyze_success(self) -> List[FeedbackInsight]:
        return [i for i in self._insights.values() if i.error < 0.3]
    def analyze_failure(self) -> List[FeedbackInsight]:
        return [i for i in self._insights.values() if i.error > 0.3]
    def get_lessons(self) -> List[str]:
        lessons = []
        for i in self._insights.values():
            lessons.extend(i.failure_reasons)
        return lessons
    def count(self) -> int: return len(self._insights)
