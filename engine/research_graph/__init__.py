"""Research Graph - knowledge graph for research entities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple

@dataclass
class GraphNode:
    node_id: str; node_type: str; label: str; properties: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class GraphEdge:
    source: str; target: str; edge_type: str; weight: float = 1.0
    def to_dict(self): return asdict(self)

class ResearchGraph:
    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
    def add_node(self, node: GraphNode) -> GraphNode:
        self._nodes[node.node_id] = node; return node
    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0) -> GraphEdge:
        edge = GraphEdge(source=source, target=target, edge_type=edge_type, weight=weight)
        self._edges.append(edge); return edge
    def get_node(self, nid: str) -> Optional[GraphNode]: return self._nodes.get(nid)
    def list_nodes(self, node_type: Optional[str] = None) -> List[GraphNode]:
        if node_type: return [n for n in self._nodes.values() if n.node_type == node_type]
        return list(self._nodes.values())
    def get_children(self, nid: str) -> List[GraphNode]:
        targets = {e.target for e in self._edges if e.source == nid}
        return [self._nodes[t] for t in targets if t in self._nodes]
    def get_parents(self, nid: str) -> List[GraphNode]:
        sources = {e.source for e in self._edges if e.target == nid}
        return [self._nodes[s] for s in sources if s in self._nodes]
    def get_edges(self, edge_type: Optional[str] = None) -> List[GraphEdge]:
        if edge_type: return [e for e in self._edges if e.edge_type == edge_type]
        return self._edges
    def count_nodes(self) -> int: return len(self._nodes)
    def count_edges(self) -> int: return len(self._edges)
    def _find_path(self, current: str, target: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
        if current == target: return path + [current]
        if current in visited: return None
        visited.add(current)
        for e in self._edges:
            if e.source == current:
                result = self._find_path(e.target, target, visited, path + [current])
                if result: return result
        return None
    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        return self._find_path(source, target, set(), [])
