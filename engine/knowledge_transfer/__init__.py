"""Knowledge Transfer Engine - transfer knowledge between domains."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class TransferredInsight:
    insight_id: str; source_domain: str; target_domain: str; concept: str
    similarity_score: float; applicability: float; description: str
    def to_dict(self):
        return asdict(self)

class KnowledgeTransferEngine:
    def __init__(self):
        self._insights: Dict[str, TransferredInsight] = {}
    def record_insight(self, insight: TransferredInsight):
        self._insights[insight.insight_id] = insight; return insight
    def concept_mapping(self, source_concepts: List[str], target_concepts: List[str]) -> List[Dict[str, Any]]:
        return [{"source": s, "target": t, "similarity": 0.5} for s in source_concepts for t in target_concepts]
    def get_insights(self) -> List[TransferredInsight]: return list(self._insights.values())
    def find_applicable(self, domain: str, min_applicability: float = 0.5) -> List[TransferredInsight]:
        return [i for i in self._insights.values() if i.target_domain == domain and i.applicability >= min_applicability]
    def count(self) -> int: return len(self._insights)
