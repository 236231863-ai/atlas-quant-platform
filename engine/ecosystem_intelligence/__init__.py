"""Ecosystem Intelligence - marketplace analytics, trends, demands."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class EcosystemReport:
    hot_solutions:List[str]=field(default_factory=list)
    industry_trends:Dict[str,float]=field(default_factory=dict)
    user_demands:List[str]=field(default_factory=list)
    asset_values:Dict[str,float]=field(default_factory=dict)
    def to_dict(self):
        return asdict(self)

class MarketplaceAnalyzer:
    def __init__(self):
        self._reports: List[EcosystemReport] = []
    def analyze(self, usage_data: Dict[str, int]) -> EcosystemReport:
        sorted_usage = sorted(usage_data.items(), key=lambda x: x[1], reverse=True)
        report = EcosystemReport(hot_solutions=[s for s,_ in sorted_usage[:5]], industry_trends={"finance":0.8,"retail":0.6}, user_demands=["data integration"], asset_values={a:float(v) for a,v in sorted_usage})
        self._reports.append(report); return report
    def get_history(self) -> List[EcosystemReport]: return self._reports
    def count(self) -> int: return len(self._reports)
