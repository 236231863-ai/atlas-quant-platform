"""News & Information Intelligence - external news understanding."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class NewsInsight:
    insight_id:str
    event:str
    topic:str
    sentiment:str="neutral"
    impact:str="medium"
    risk:str="medium"
    related_assets:List[str]=field(default_factory=list)
    confidence:float=0.5
    def to_dict(self):
        return asdict(self)

class NewsIntelligenceEngine:
    def __init__(self):
        self._insights: Dict[str, NewsInsight] = {}
    def record_insight(self, insight: NewsInsight):
        self._insights[insight.insight_id] = insight
        return insight
    def analyze_topic(self, topic: str) -> List[NewsInsight]:
        return [i for i in self._insights.values() if topic.lower() in i.topic.lower()]
    def get_insights_by_risk(self, risk: str) -> List[NewsInsight]:
        return [i for i in self._insights.values() if i.risk == risk]
    def count(self) -> int: return len(self._insights)
