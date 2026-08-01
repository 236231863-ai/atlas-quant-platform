"""Personal AI Research Assistant v2 - upgraded with memory, recommendations, explainability."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AIRecommendation:
    rec_id:str
    content:str
    reasoning:str
    confidence:float=0.5
    risk:str="low"
    source_data:str=""
    def to_dict(self):
        return asdict(self)

class PersonalAIAssistantV2:
    def __init__(self):
        self._memory: Dict[str, List[Dict[str, Any]]] = {}
        self._preferences: Dict[str, Dict[str, Any]] = {}
    def remember(self, uid: str, event: Dict[str, Any]):
        if uid not in self._memory: self._memory[uid] = []
        self._memory[uid].append(event)
    def suggest(self, uid: str) -> List[AIRecommendation]:
        hist = self._memory.get(uid, [])
        if not hist: return [AIRecommendation("1","Start your first analysis to receive personalized recommendations","Based on your empty history",0.3,"low","none")]
        recs = []
        analysis_count = len(hist)
        recs.append(AIRecommendation("2",f"You have completed {analysis_count} analyses. Consider trying backtesting.","Based on your analysis history",0.7,"low","user_history"))
        return recs
    def get_history(self, uid: str) -> List[Dict[str, Any]]: return self._memory.get(uid, [])
