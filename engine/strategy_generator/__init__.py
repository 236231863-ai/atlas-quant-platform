"""Strategy Generator Foundation - generate strategies from knowledge."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set

@dataclass
class StrategyCandidate:
    strategy_id: str; name: str; strategy_type: str; params: Dict[str, Any]
    source: str = "knowledge_base"; confidence: float = 0.5
    def to_dict(self): return asdict(self)

class StrategyGenerator:
    def __init__(self):
        self._patterns: List[Dict[str, Any]] = []

    def register_pattern(self, feature: str, pattern: str, success_rate: float):
        self._patterns.append({"feature":feature,"pattern":pattern,"success_rate":success_rate})

    def generate_from_kb(self, tags: List[str]) -> List[StrategyCandidate]:
        candidates = []
        for p in self._patterns:
            if any(t in p["pattern"].lower() for t in tags):
                candidates.append(StrategyCandidate(
                    strategy_id=f"kb_{p['feature']}_{len(candidates)+1}",
                    name=f"{p['feature'].title()}BalancedV{len(candidates)+1}",
                    strategy_type="gap_based", params={"feature":p["feature"]},
                    source="knowledge_base", confidence=p["success_rate"]))
        return candidates

    def generate_from_experiments(self, experiments: List[Dict[str, Any]]) -> List[StrategyCandidate]:
        candidates = []
        for e in experiments:
            metrics = e.get("metrics", {})
            if metrics.get("sharpe_ratio", 0) > 0.5:
                candidates.append(StrategyCandidate(
                    strategy_id=f"hist_{e.get('strategy','?')}_{len(candidates)+1}",
                    name=f"DerivedV{len(candidates)+1}", strategy_type="gap_based",
                    params=e.get("params", {}), source="historical", confidence=0.4))
        return candidates

    def list_patterns(self) -> List[Dict[str, Any]]: return self._patterns
