"""Intelligence Evaluation Engine - evaluate intelligence quality and value."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class IntelligenceScore: accuracy:float=0.0; calibration:float=0.0; confidence:float=0.0; decision_quality:float=0.0; overall:float=0.0; def compute(self): self.overall=round((self.accuracy+self.calibration+self.confidence+self.decision_quality)/4,4); def to_dict(self):return asdict(self)

class IntelligenceEvaluationEngine:
    def __init__(self): self._scores: List[IntelligenceScore] = []
    def evaluate_prediction(self, accuracy: float, calibration: float, confidence: float) -> IntelligenceScore:
        s = IntelligenceScore(accuracy=accuracy, calibration=calibration, confidence=confidence, decision_quality=(accuracy+calibration)/2); s.compute()
        self._scores.append(s); return s
    def evaluate_decision(self, suggestions: int, adopted: int) -> float:
        return round(adopted/max(suggestions,1), 4)
    def get_history(self) -> List[IntelligenceScore]: return self._scores
    def count(self) -> int: return len(self._scores)
