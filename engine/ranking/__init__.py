"""Research Ranking System - evaluate and rank research contributions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class RankScore:
    researcher_id: str; research_quality: float=0.0; backtest_quality: float=0.0
    risk_control: float=0.0; community_contribution: float=0.0; knowledge_contribution: float=0.0
    def overall(self): return round((self.research_quality+self.backtest_quality+self.risk_control+self.community_contribution+self.knowledge_contribution)/5, 4)
    def to_dict(self): return asdict(self)

class ResearchRankEngine:
    def __init__(self): self._scores: Dict[str, RankScore] = {}
    def evaluate(self, score: RankScore): self._scores[score.researcher_id] = score; return score
    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted([{"researcher_id": s.researcher_id, "score": s.overall()} for s in self._scores.values()],
                     key=lambda x: x["score"], reverse=True)
    def top_strategies(self) -> List[Dict[str, Any]]: return self.leaderboard()[:10]
    def get_score(self, rid: str) -> Optional[RankScore]: return self._scores.get(rid)
    def count(self) -> int: return len(self._scores)
