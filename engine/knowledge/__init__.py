"""Research Knowledge Base - long-term research memory."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

@dataclass
class KnowledgeRecord:
    id: str; type: str; content: str; tags: List[str] = field(default_factory=list)
    confidence: float = 0.5; parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return asdict(self)

class KnowledgeBase:
    def __init__(self):
        self._records: Dict[str, KnowledgeRecord] = {}
    def add(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self._records[record.id] = record; return record
    def get(self, rid: str) -> Optional[KnowledgeRecord]: return self._records.get(rid)
    def list(self) -> List[KnowledgeRecord]: return list(self._records.values())
    def search(self, query: str) -> List[KnowledgeRecord]:
        q = query.lower()
        return [r for r in self._records.values()
                if q in r.content.lower() or any(q in t.lower() for t in r.tags)]
    def count(self) -> int: return len(self._records)
    def by_tag(self, tag: str) -> List[KnowledgeRecord]:
        return [r for r in self._records.values() if tag in r.tags]
    def by_type(self, tp: str) -> List[KnowledgeRecord]:
        return [r for r in self._records.values() if r.type == tp]
    def similar_experiments(self, record_id: str, max_results: int = 5) -> List[KnowledgeRecord]:
        src = self.get(record_id)
        if not src: return []
        scored = []
        for r in self._records.values():
            if r.id == record_id: continue
            shared = len(set(src.tags) & set(r.tags))
            if shared > 0: scored.append((shared, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:max_results]]

class ResearchMemory:
    def __init__(self):
        self._kb = KnowledgeBase()
    @property
    def knowledge_base(self):
        return self._kb
    def record_hypothesis(self, hid: str, content: str, tags: List[str], confidence: float = 0.3) -> KnowledgeRecord:
        return self._kb.add(KnowledgeRecord(id=hid, type="hypothesis", content=content, tags=tags, confidence=confidence))
    def record_experiment(self, eid: str, content: str, tags: List[str], parent: Optional[str] = None) -> KnowledgeRecord:
        return self._kb.add(KnowledgeRecord(id=eid, type="experiment", content=content, tags=tags, parent_id=parent))
    def record_conclusion(self, cid: str, content: str, tags: List[str], confidence: float = 0.7) -> KnowledgeRecord:
        return self._kb.add(KnowledgeRecord(id=cid, type="conclusion", content=content, tags=tags, confidence=confidence))

class ExperimentArchive:
    def __init__(self):
        self._archive: List[KnowledgeRecord] = []
    def archive(self, record: KnowledgeRecord):
        self._archive.append(record)
    def list(self) -> List[KnowledgeRecord]: return self._archive
    def count(self) -> int: return len(self._archive)
    def find_by_tag(self, tag: str) -> List[KnowledgeRecord]:
        return [r for r in self._archive if tag in r.tags]
