"""Product Feedback Learning System - learn from user feedback."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class FeatureValueScore: feature:str; value_score:float=0.0; usage_count:int=0; def to_dict(self):return asdict(self)
@dataclass
class ProductInsight: insight_id:str; feature:str; recommendation:str; confidence:float=0.5; def to_dict(self):return asdict(self)

class ProductKnowledgeBase:
    def __init__(self): self._records: Dict[str, FeatureValueScore] = {}
    def record(self, r: FeatureValueScore): self._records[r.feature] = r; return r
    def get_top_features(self, n: int = 5) -> List[FeatureValueScore]:
        return sorted(self._records.values(), key=lambda r: r.value_score, reverse=True)[:n]
    def count(self) -> int: return len(self._records)

class FeedbackLearningEngine:
    def __init__(self): self._kb = ProductKnowledgeBase()
    def learn(self, feature: str, success: bool):
        score = self._kb._records.get(feature, FeatureValueScore(feature=feature))
        score.usage_count += 1; score.value_score = (score.value_score * (score.usage_count - 1) + (1.0 if success else 0.0)) / score.usage_count
        self._kb.record(score)
    def get_kb(self): return self._kb
