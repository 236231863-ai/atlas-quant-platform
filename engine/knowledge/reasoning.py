"""Research Memory Upgrade - store reasoning, success/failure reasons, insights."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class SuccessReason:
    strategy_id: str; reason: str; conditions: List[str]; success_rate: float = 0.0
    def to_dict(self):
        return asdict(self)

@dataclass
class FailureReason:
    strategy_id: str; reason: str; conditions: List[str]; failure_rate: float = 0.0
    def to_dict(self):
        return asdict(self)

@dataclass
class StrategyCondition:
    feature: str; condition: str; threshold: float; direction: str = "above"
    def to_dict(self):
        return asdict(self)

@dataclass
class ResearchInsight:
    insight_id: str; content: str; related_strategies: List[str]; confidence: float = 0.5
    insight_type: str = "general"
    def to_dict(self):
        return asdict(self)

class ResearchMemoryUpgrade:
    def __init__(self):
        self._success: List[SuccessReason] = []; self._failures: List[FailureReason] = []
        self._conditions: List[StrategyCondition] = []; self._insights: List[ResearchInsight] = []

    def record_success(self, sr: SuccessReason):
        self._success.append(sr)
    def record_failure(self, fr: FailureReason):
        self._failures.append(fr)
    def record_condition(self, sc: StrategyCondition):
        self._conditions.append(sc)
    def record_insight(self, ri: ResearchInsight):
        self._insights.append(ri)

    def get_successes(self) -> List[SuccessReason]: return self._success
    def get_failures(self) -> List[FailureReason]: return self._failures
    def get_insights(self) -> List[ResearchInsight]: return self._insights
    def find_by_strategy(self, sid: str) -> Dict[str, Any]:
        success = next((s for s in self._success if s.strategy_id == sid), None)
        failure = next((f for f in self._failures if f.strategy_id == sid), None)
        return {"strategy_id": sid, "success": success.to_dict() if success else None,
                "failure": failure.to_dict() if failure else None}
