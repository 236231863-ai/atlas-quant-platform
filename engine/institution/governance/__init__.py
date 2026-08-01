"""Research Governance System - define institution rules."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchPolicy:
    policy_id: str; name: str; rules: List[str]; scope: str; priority: int = 5; status: str = "active"
    def to_dict(self):
        return asdict(self)

class ResearchGovernanceEngine:
    def __init__(self):
        self._policies: Dict[str, ResearchPolicy] = {}
    def create_policy(self, policy: ResearchPolicy):
        self._policies[policy.policy_id] = policy
        return policy
    def evaluate_compliance(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        violations = []
        for p in self._policies.values():
            if p.status != "active": continue
            for rule in p.rules:
                if rule not in str(activity): violations.append({"policy": p.name, "rule": rule})
        return {"compliant": len(violations) == 0, "violations": violations, "checked_policies": len(self._policies)}
    def approve_research(self, proposal_id: str) -> bool:
        return len(self._policies) == 0 or len([p for p in self._policies.values() if p.status == "active"]) > 0
    def list_policies(self) -> List[ResearchPolicy]: return list(self._policies.values())
    def count(self) -> int: return len(self._policies)
