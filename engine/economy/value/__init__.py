"""Research Value Evaluation Engine - evaluate scientific value."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchValueScore:
    asset_id: str; innovation: float = 0.0; performance: float = 0.0
    knowledge: float = 0.0; impact: float = 0.0; total_score: float = 0.0
    def compute(self):
        self.total_score = round((self.innovation+self.performance+self.knowledge+self.impact)/4, 4)
    def to_dict(self):
        return asdict(self)

class ResearchValueEngine:
    def __init__(self):
        self._scores: Dict[str, ResearchValueScore] = {}
    def evaluate(self, score: ResearchValueScore):
        score.compute(); self._scores[score.asset_id] = score; return score
    def compare(self, id1: str, id2: str) -> Dict[str, Any]:
        s1, s2 = self._scores.get(id1), self._scores.get(id2)
        if not s1 or not s2: return {"error":"asset not found"}
        return {"asset1": s1.total_score, "asset2": s2.total_score, "better": id1 if s1.total_score > s2.total_score else id2}
    def rank(self) -> List[Dict[str, Any]]:
        sorted_scores = sorted(self._scores.values(), key=lambda s: s.total_score, reverse=True)
        return [{"asset_id": s.asset_id, "score": s.total_score} for s in sorted_scores]
    def get_score(self, asset_id: str) -> Optional[ResearchValueScore]: return self._scores.get(asset_id)
    def count(self) -> int: return len(self._scores)
