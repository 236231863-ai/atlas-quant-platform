"""Decision Memory System - record past decisions, outcomes, lessons learned."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DecisionRecord:
    decision_id:str
    decision:str
    prediction:str
    actual_result:str
    accuracy:float=0.0
    lesson:str=""
    def to_dict(self):
        return asdict(self)

class DecisionMemorySystem:
    def __init__(self):
        self._records: Dict[str, DecisionRecord] = {}
    def record(self, record: DecisionRecord):
        self._records[record.decision_id] = record
        return record
    def get_effective(self, threshold: float=0.7) -> List[DecisionRecord]:
        return [r for r in self._records.values() if r.accuracy >= threshold]
    def get_failed(self, threshold: float=0.3) -> List[DecisionRecord]:
        return [r for r in self._records.values() if r.accuracy <= threshold]
    def get_lessons(self) -> List[str]:
        return [r.lesson for r in self._records.values() if r.lesson]
    def count(self) -> int: return len(self._records)
