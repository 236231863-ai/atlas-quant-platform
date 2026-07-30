"""Research Discovery Engine - automatically discover research opportunities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
import math

@dataclass
class DiscoveryReport:
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    total_opportunities: int = 0; top_priority: float = 0.0
    def to_dict(self): return asdict(self)

class ResearchDiscoveryEngine:
    @staticmethod
    def detect_feature_anomalies(historical_features: List[Dict[str, float]], recent_features: Dict[str, float]) -> List[Dict[str, Any]]:
        anomalies = []
        for key, recent_val in recent_features.items():
            hist_vals = [h.get(key, 0) for h in historical_features if key in h]
            if not hist_vals: continue
            mean = sum(hist_vals) / len(hist_vals)
            std = math.sqrt(sum((v - mean)**2 for v in hist_vals) / len(hist_vals)) if len(hist_vals) > 1 else 0
            if std > 0:
                z = (recent_val - mean) / std
                if abs(z) > 2.0:
                    anomalies.append({"feature": key, "z_score": round(z, 2), "direction": "increase" if z > 0 else "decrease",
                                      "recent": round(recent_val, 4), "historical_mean": round(mean, 4)})
        return anomalies

    @staticmethod
    def detect_strategy_degradation(performance_history: List[Dict[str, float]], window: int = 10) -> List[Dict[str, Any]]:
        if len(performance_history) < window * 2: return []
        recent = [p.get("sharpe_ratio", 0) for p in performance_history[-window:]]
        earlier = [p.get("sharpe_ratio", 0) for p in performance_history[-(window*2):-window]]
        if not recent or not earlier: return []
        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)
        declines = []
        if recent_avg < earlier_avg * 0.7:
            declines.append({"type": "sharpe_decline", "recent_avg": round(recent_avg, 4), "earlier_avg": round(earlier_avg, 4),
                             "decline_pct": round((1 - recent_avg / earlier_avg) * 100, 1)})
        recent_dd = [p.get("max_drawdown", 0) for p in performance_history[-window:]]
        if recent_dd and max(recent_dd) > 20:
            declines.append({"type": "drawdown_increase", "max_drawdown": max(recent_dd)})
        return declines

    @staticmethod
    def score_opportunity(anomalies: List[Dict[str, Any]], degradations: List[Dict[str, Any]]) -> DiscoveryReport:
        discoveries = []
        for a in anomalies:
            priority = min(1.0, abs(a.get("z_score", 0)) / 5.0)
            discoveries.append({"type": "feature_anomaly", "target": a["feature"], "priority": round(priority, 2),
                                "recommendation": f"Investigate {a['feature']} {a['direction']} (z={a['z_score']})"})
        for d in degradations:
            priority = 0.8 if d["type"] == "sharpe_decline" else 0.7
            discoveries.append({"type": "strategy_degradation", "target": d["type"], "priority": priority,
                                "recommendation": f"Review strategy: {d.get('decline_pct',0)}% decline"})
        top = max([d.get("priority", 0) for d in discoveries]) if discoveries else 0.0
        return DiscoveryReport(discoveries=discoveries, total_opportunities=len(discoveries), top_priority=round(top, 2))
