"""Creator Intelligence - optimize creator success and satisfaction."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CreatorInsight:
    creator_id:str
    engagement_score:float=0.0
    revenue_generated:float=0.0
    growth_potential:float=0.0
    recommended_actions:List[str]=field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class CreatorIntelligence:
    def __init__(self):
        self._insights: Dict[str, CreatorInsight] = {}
    def analyze(self, cid: str) -> CreatorInsight:
        insight = CreatorInsight(creator_id=cid, engagement_score=0.75, revenue_generated=5000, growth_potential=0.8,
            recommended_actions=["Publish more solutions","Engage with enterprise buyers"])
        self._insights[cid] = insight; return insight
    def get_top_creators(self, n: int=5) -> List[CreatorInsight]:
        return sorted(self._insights.values(), key=lambda c: c.revenue_generated, reverse=True)[:n]
    def count(self) -> int: return len(self._insights)
