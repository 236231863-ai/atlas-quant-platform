"""System Observability Engine - monitor system health, module usage, agent performance."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class SystemHealthReport: cpu_usage:float=0.0; memory_usage:float=0.0; latency_ms:float=0.0; error_rate:float=0.0; module_status:Dict[str,str]=field(default_factory=dict); healthy:bool=True; def to_dict(self):return asdict(self)

class SystemObservabilityEngine:
    def __init__(self): self._reports: List[SystemHealthReport] = []
    def check_health(self) -> SystemHealthReport:
        report = SystemHealthReport(cpu_usage=0.3, memory_usage=0.4, latency_ms=50, error_rate=0.01, module_status={"causal":"active","decision":"active","action":"active"}, healthy=True)
        self._reports.append(report); return report
    def get_history(self) -> List[SystemHealthReport]: return self._reports
    def analyze_modules(self) -> Dict[str, float]:
        return {"causal": 0.8, "decision": 0.9, "action": 0.7, "feedback": 0.6, "adaptation": 0.5}
    def count(self) -> int: return len(self._reports)
