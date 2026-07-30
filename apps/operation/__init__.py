"""Operation Center - monitor users, tasks, system load, AI usage, resources."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class OperationMetrics: user_count:int=0; task_count:int=0; system_load:float=0.0; ai_usage:float=0.0; resource_usage:float=0.0; def to_dict(self):return asdict(self)

class OperationInsightEngine:
    def __init__(self): self._metrics: List[OperationMetrics] = []
    def collect(self, m: OperationMetrics): self._metrics.append(m); return m
    def detect_anomalies(self) -> List[str]:
        if not self._metrics: return []
        latest = self._metrics[-1]; issues = []
        if latest.system_load > 0.8: issues.append("High system load detected")
        if latest.ai_usage > 0.9: issues.append("AI capacity near limit")
        return issues
    def get_history(self) -> List[OperationMetrics]: return self._metrics
    def count(self) -> int: return len(self._metrics)
