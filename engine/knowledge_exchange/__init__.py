"""Research Knowledge Exchange - share discoveries across communities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class KnowledgeExchangeRecord:
    record_id: str; source: str; receiver: str; reason: str; confidence: float = 0.5
    impact: float = 0.0; knowledge_type: str = "insight"
    def to_dict(self): return asdict(self)

class KnowledgeExchangeEngine:
    def __init__(self): self._records: Dict[str, KnowledgeExchangeRecord] = {}
    def publish_insight(self, record: KnowledgeExchangeRecord):
        self._records[record.record_id] = record; return record
    def request_knowledge(self, topic: str) -> List[KnowledgeExchangeRecord]:
        return [r for r in self._records.values() if topic.lower() in r.reason.lower()]
    def match_research(self, source: str, min_confidence: float = 0.5) -> List[KnowledgeExchangeRecord]:
        return [r for r in self._records.values() if r.source == source and r.confidence >= min_confidence]
    def get_records(self) -> List[KnowledgeExchangeRecord]: return list(self._records.values())
    def count(self) -> int: return len(self._records)
