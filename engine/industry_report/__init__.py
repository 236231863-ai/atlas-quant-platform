"""Industry Report Center - generate industry-specific reports."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class IndustryReport: report_id:str; industry:str; report_type:str="industry"; title:str=""; content:str=""; format:str="markdown"; def to_dict(self):return asdict(self)

class IndustryReportGenerator:
    def __init__(self): self._reports: Dict[str, IndustryReport] = {}
    def generate(self, r: IndustryReport): self._reports[r.report_id] = r; return r
    def list_by_industry(self, industry: str) -> List[IndustryReport]:
        return [r for r in self._reports.values() if r.industry == industry]
    def get_report(self, rid: str) -> Optional[IndustryReport]: return self._reports.get(rid)
    def count(self) -> int: return len(self._reports)
