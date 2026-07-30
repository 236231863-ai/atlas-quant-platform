"""Quality Gate Engine - continuous quality validation and release gates."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ReleaseQualityReport: code_changes:int=0; api_compatible:bool=True; module_impact:List[str]=field(default_factory=list); test_coverage:float=0.0; gate_passed:bool=True; def to_dict(self):return asdict(self)

class QualityGateEngine:
    def __init__(self): self._reports: List[ReleaseQualityReport] = []
    def check_release(self, changes: int, coverage: float) -> ReleaseQualityReport:
        r=ReleaseQualityReport(code_changes=changes, test_coverage=coverage, gate_passed=coverage>=0.8); self._reports.append(r); return r
    def get_history(self) -> List[ReleaseQualityReport]: return self._reports
    def count(self) -> int: return len(self._reports)
