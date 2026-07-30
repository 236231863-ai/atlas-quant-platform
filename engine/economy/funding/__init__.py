"""Research Funding System - allocate research budget."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchFund:
    project_id: str; budget: float; risk: float; expected_value: float; status: str = "proposed"
    allocated: float = 0.0
    def to_dict(self): return asdict(self)

class ResearchFundingManager:
    def __init__(self): self._funds: Dict[str, ResearchFund] = {}
    def submit_project(self, fund: ResearchFund): self._funds[fund.project_id] = fund; return fund
    def evaluate_project(self, pid: str) -> Optional[Dict[str, Any]]:
        f = self._funds.get(pid)
        if not f: return None
        score = f.expected_value / max(f.risk, 0.01)
        return {"project_id": pid, "score": round(score, 2), "recommendation": "approved" if score > 5 else "rejected"}
    def allocate_budget(self, pid: str, budget: float) -> bool:
        f = self._funds.get(pid)
        if not f: return False
        f.allocated = budget; f.status = "funded"; return True
    def list_funds(self) -> List[ResearchFund]: return list(self._funds.values())
    def count(self) -> int: return len(self._funds)
