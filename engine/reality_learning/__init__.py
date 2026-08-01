"""Reality Learning Engine - learn from real world outcomes."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class PredictionRecord:
    record_id:str
    prediction:str
    actual_result:str
    error:float=0.0
    reason:str=""
    timestamp:str=""
    def to_dict(self):
        return asdict(self)
@dataclass
class RealityLearningReport:
    records:List[PredictionRecord]=field(default_factory=list)
    avg_error:float=0.0
    improvement_suggestions:List[str]=field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class RealityLearningEngine:
    def __init__(self):
        self._records: Dict[str, PredictionRecord] = {}
    def record(self, record: PredictionRecord):
        self._records[record.record_id] = record
        return record
    def analyze(self) -> RealityLearningReport:
        if not self._records: return RealityLearningReport()
        errors = [r.error for r in self._records.values()]
        avg = sum(errors)/len(errors)
        suggestions = ["Reduce prediction threshold"] if avg > 0.3 else ["Current prediction quality acceptable"]
        return RealityLearningReport(records=list(self._records.values()), avg_error=round(avg,4), improvement_suggestions=suggestions)
    def get_success_factors(self) -> List[str]:
        return [r.reason for r in self._records.values() if r.error < 0.2]
    def count(self) -> int: return len(self._records)
