"""Personal AI Research Assistant - personalized research companion."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AISuggestion:
    suggestion_id: str; content: str; category: str; priority: str="medium"
    def to_dict(self):
        return asdict(self)

class PersonalResearchAssistant:
    def __init__(self):
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._suggestions: Dict[str, List[AISuggestion]] = {}
    def remember_analysis(self, uid: str, analysis: Dict[str, Any]):
        if uid not in self._history: self._history[uid] = []
        self._history[uid].append(analysis)
    def get_suggestions(self, uid: str) -> List[AISuggestion]:
        hist = self._history.get(uid, [])
        if not hist: return [AISuggestion("1","Start your first analysis","onboarding","high")]
        suggestions = []
        strategies_used = set(h.get("strategy","") for h in hist)
        if len(strategies_used) == 1:
            s = list(strategies_used)[0]
            suggestions.append(AISuggestion("2",f"Try comparing {s} with a different strategy","suggestion","medium"))
        if len(hist) > 5:
            suggestions.append(AISuggestion("3","Would you like to run a backtest?","reminder","low"))
        return suggestions
    def get_history(self, uid: str) -> List[Dict[str, Any]]: return self._history.get(uid, [])
