"""Adaptive Strategy Engine - automatically adjust based on feedback."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AdaptationResult: parameter:str; before:float; after:float; adjustment:float; reason:str; def to_dict(self):return asdict(self)

class AdaptiveStrategyEngine:
    def __init__(self): self._adaptations: List[AdaptationResult] = []
    def adjust_parameter(self, param: str, current: float, feedback_error: float, learning_rate: float=0.1) -> AdaptationResult:
        adjustment = -feedback_error * learning_rate
        new_val = max(0.0, min(1.0, current + adjustment))
        result = AdaptationResult(parameter=param, before=round(current,4), after=round(new_val,4), adjustment=round(adjustment,4), reason=f"Feedback based adjustment (error={feedback_error:.2f})")
        self._adaptations.append(result); return result
    def mutate_strategy(self, strategy: Dict[str,Any], feedback: List[FeedbackInsight]) -> Dict[str,Any]:
        mutated = dict(strategy)
        for f in feedback:
            for k in mutated:
                if isinstance(mutated[k], (int,float)):
                    mutated[k] = mutated[k] * (1 + f.error * 0.1)
        return mutated
    def get_history(self) -> List[AdaptationResult]: return self._adaptations
    def count(self) -> int: return len(self._adaptations)
