"""Strategy Evolution Engine - generate new strategy generations."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

@dataclass
class EvolutionNode:
    strategy_id: str; generation: int; parent_id: Optional[str]; mutation_type: str
    parameters: Dict[str, Any]; performance: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self):
        return asdict(self)

@dataclass
class EvolutionGraph:
    nodes: List[EvolutionNode] = field(default_factory=list)
    def add_node(self, node: EvolutionNode):
        self.nodes.append(node)
        return node
    def get_lineage(self, strategy_id: str) -> List[EvolutionNode]:
        result = []; current = strategy_id
        while current:
            node = next((n for n in self.nodes if n.strategy_id == current), None)
            if node: result.append(node); current = node.parent_id
            else: current = None
        return result
    def count(self) -> int: return len(self.nodes)

class StrategyEvolutionEngine:
    def __init__(self):
        self._graph = EvolutionGraph()
    @property
    def graph(self):
        return self._graph

    def create_initial(self, strategy_id: str, params: Dict[str, Any]) -> EvolutionNode:
        node = EvolutionNode(strategy_id=strategy_id, generation=1, parent_id=None,
                             mutation_type="initial", parameters=params)
        return self._graph.add_node(node)

    def mutate(self, child_id: str, parent_id: str, mutation: str, params: Dict[str, Any]) -> EvolutionNode:
        parent = next((n for n in self._graph.nodes if n.strategy_id == parent_id), None)
        gen = (parent.generation + 1) if parent else 1
        node = EvolutionNode(strategy_id=child_id, generation=gen, parent_id=parent_id,
                             mutation_type=mutation, parameters=params)
        return self._graph.add_node(node)

    def get_best_performing(self, metric: str = "sharpe_ratio") -> Optional[EvolutionNode]:
        scored = [(n, n.performance.get(metric, -999)) for n in self._graph.nodes]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None
