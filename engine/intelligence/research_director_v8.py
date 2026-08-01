"""Research Director v8 - world-aware research orchestration."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

class ResearchDirectorV8:
    def __init__(self):
        self._observations: List[Dict[str, Any]] = []
        self._goals: List[str] = []
    def observe_world(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        self._observations.extend(signals); return {"observations": len(signals), "total_observed": len(self._observations)}
    def detect_change(self) -> List[Dict[str, Any]]:
        if not self._observations: return [{"type": "no_change", "confidence": 1.0}]
        changes = [s for s in self._observations if s.get("severity") in ["high","critical"]]
        return changes if changes else [{"type": "stable", "confidence": 0.9}]
    def generate_goal(self, changes: List[Dict[str, Any]]) -> str:
        if not changes: return "Continue monitoring for research opportunities"
        return f"Investigate {len(changes)} detected changes in research environment"
    def observe_count(self) -> int: return len(self._observations)
