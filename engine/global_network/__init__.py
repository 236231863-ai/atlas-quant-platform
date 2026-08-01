"""Global Research Node Network - connect distributed research nodes."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class NetworkNode:
    node_id: str; node_type: str; status: str = "idle"; task_count: int = 0
    capabilities: List[str] = field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class ResearchNodeNetwork:
    def __init__(self):
        self._nodes: Dict[str, NetworkNode] = {}
    def register_node(self, node: NetworkNode):
        self._nodes[node.node_id] = node
        return node
    def assign_task(self, node_id: str) -> bool:
        node = self._nodes.get(node_id)
        if not node: return False
        node.status = "working"; node.task_count += 1; return True
    def monitor_node(self, node_id: str) -> Optional[NetworkNode]: return self._nodes.get(node_id)
    def aggregate_results(self) -> Dict[str, Any]:
        total = len(self._nodes); working = sum(1 for n in self._nodes.values() if n.status == "working")
        idle = sum(1 for n in self._nodes.values() if n.status == "idle")
        offline = sum(1 for n in self._nodes.values() if n.status == "offline")
        return {"total": total, "working": working, "idle": idle, "offline": offline, "utilization": round(working/total, 2) if total > 0 else 0}
    def list_nodes(self) -> List[NetworkNode]: return list(self._nodes.values())
    def count(self) -> int: return len(self._nodes)
