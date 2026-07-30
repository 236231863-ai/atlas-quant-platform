"""Product API Layer - convert research into user services."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

@dataclass
class AnalysisRequest:
    lottery_code: str = "dlt"; mode: str = "basic"; strategy: str = "balanced"
    parameters: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class AnalysisReport:
    report_id: str; summary: str; analysis_type: str; results: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    disclaimer: str = "Statistical analysis only. No guarantee of future outcomes."
    def to_dict(self): return asdict(self)

class ProductAPI:
    def __init__(self): self._reports: Dict[str, AnalysisReport] = {}
    def dashboard(self) -> Dict[str, Any]:
        return {"status": "online", "version": "2.1.1", "lotteries": ["dlt","ssq"], "total_reports": len(self._reports)}
    def analyze(self, request: AnalysisRequest) -> AnalysisReport:
        rid = f"report_{len(self._reports)+1}"
        report = AnalysisReport(report_id=rid, summary=f"Analysis of {request.lottery_code} using {request.mode} mode",
            analysis_type=request.mode, results={"lottery":request.lottery_code,"strategy":request.strategy})
        self._reports[rid] = report; return report
    def get_report(self, rid: str) -> Optional[AnalysisReport]: return self._reports.get(rid)
    def list_reports(self) -> List[AnalysisReport]: return list(self._reports.values())
    def count(self) -> int: return len(self._reports)
