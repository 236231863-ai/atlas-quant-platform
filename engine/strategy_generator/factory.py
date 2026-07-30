"""Strategy Factory - automatically generate strategy candidates from patterns."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.strategy_generator import StrategyCandidate

@dataclass
class StrategyTemplate:
    template_id: str; name: str; base_type: str; parameter_schema: Dict[str, Any]
    def to_dict(self): return asdict(self)

class StrategyFactory:
    def __init__(self):
        self._templates: List[StrategyTemplate] = []
        self._mutations: List[Dict[str, Any]] = []

    def register_template(self, template: StrategyTemplate):
        self._templates.append(template)

    def generate_from_pattern(self, pattern_type: str, features: List[str]) -> List[StrategyCandidate]:
        candidates = []
        for feat in features:
            candidates.append(StrategyCandidate(
                strategy_id=f"factory_{feat}_{len(candidates)+1}",
                name=f"{feat.title()}StrategyV{len(candidates)+1}",
                strategy_type="gap_based", params={"feature":feat},
                source="strategy_factory", confidence=0.6))
        return candidates

    def mutate_parameters(self, candidate: StrategyCandidate, mutation_factor: float = 0.1) -> StrategyCandidate:
        mutated = dict(candidate.params)
        for k, v in mutated.items():
            if isinstance(v, (int, float)):
                mutated[k] = v * (1 + mutation_factor)
        return StrategyCandidate(strategy_id=f"{candidate.strategy_id}_mut",
            name=f"{candidate.name}_M", strategy_type=candidate.strategy_type,
            params=mutated, source="mutation", confidence=candidate.confidence * 0.9)

    def crossover(self, parent1: StrategyCandidate, parent2: StrategyCandidate) -> StrategyCandidate:
        combined = dict(parent1.params)
        combined.update(parent2.params)
        return StrategyCandidate(strategy_id=f"cross_{parent1.strategy_id}_{parent2.strategy_id}",
            name=f"Cross_{parent1.name}_{parent2.name}", strategy_type=parent1.strategy_type,
            params=combined, source="crossover", confidence=(parent1.confidence + parent2.confidence) / 2)

    def list_templates(self) -> List[StrategyTemplate]: return self._templates
    def count_templates(self) -> int: return len(self._templates)
