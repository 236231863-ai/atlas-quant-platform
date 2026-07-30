"""AI Research Director - coordinate research, detect duplicates, recommend milestones."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from engine.research_graph import ResearchGraph

class ResearchDirector:
    def __init__(self):
        self._research_graph = ResearchGraph()
        self._experiment_history: List[Dict[str, Any]] = []

    def generate_objectives(self, history: List[Dict[str, Any]]) -> List[str]:
        if not history: return ["Establish baseline performance", "Test multiple strategy types", "Evaluate risk metrics"]
        metrics_list = [e.get("metrics", {}) for e in history]
        avg_sharpe = sum(m.get("sharpe_ratio", 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0
        objectives = []
        if avg_sharpe < 0.5: objectives.append("Improve risk-adjusted returns above 0.5 Sharpe")
        if self._detect_duplicates(history): objectives.append("Reduce duplicate experiments")
        objectives.append(f"Complete {min(20, len(history)+5)} total experiments for statistical significance")
        return objectives

    def _detect_duplicates(self, history: List[Dict[str, Any]]) -> bool:
        seen = set()
        for e in history:
            key = str(e.get("params", {}))
            if key in seen: return True
            seen.add(key)
        return False

    def summarize_history(self, experiments: List[Dict[str, Any]]) -> str:
        if not experiments: return "No experiments conducted yet."
        metrics_list = [e.get("metrics", {}) for e in experiments]
        avg_sharpe = sum(m.get("sharpe_ratio", 0) for m in metrics_list) / len(metrics_list)
        avg_roi = sum(m.get("roi", 0) for m in metrics_list) / len(metrics_list)
        unique_params = len(set(str(e.get("params", {})) for e in experiments))
        return (f"Conducted {len(experiments)} experiments ({unique_params} unique parameter sets). "
                f"Avg Sharpe: {avg_sharpe:.2f}, Avg ROI: {avg_roi:.1f}%. "
                f"Duplicates detected: {len(experiments) - unique_params}")

    def recommend_next_milestone(self, experiments: List[Dict[str, Any]]) -> str:
        if not experiments: return "Phase 1: Explore baseline strategies"
        n = len(experiments)
        if n < 5: return f"Phase 1: Complete baseline testing ({n}/5 experiments)"
        elif n < 15: return "Phase 2: Optimize best-performing strategy"
        elif n < 30: return "Phase 3: Multi-strategy portfolio optimization"
        else: return "Phase 4: Advanced research with automated loops"

    @property
    def research_graph(self): return self._research_graph
