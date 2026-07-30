"""Dataset Versioning System - track data versions for experiments."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class DatasetRecord:
    dataset_id: str; version: str; source: str; hash: str
    feature_schema: List[str]; created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    description: str = ""; size: int = 0
    def to_dict(self): return asdict(self)

class DatasetRegistry:
    def __init__(self): self._datasets: Dict[str, DatasetRecord] = {}
    def register(self, record: DatasetRecord) -> DatasetRecord:
        self._datasets[record.dataset_id] = record; return record
    def get(self, dataset_id: str) -> Optional[DatasetRecord]: return self._datasets.get(dataset_id)
    def list(self) -> List[DatasetRecord]: return list(self._datasets.values())
    def compare(self, id1: str, id2: str) -> Dict[str, Any]:
        d1, d2 = self.get(id1), self.get(id2)
        if not d1 or not d2: return {"error":"Dataset not found"}
        return {"same_version":d1.version==d2.version,"same_hash":d1.hash==d2.hash,
                "same_schema":d1.feature_schema==d2.feature_schema,"version1":d1.version,"version2":d2.version}
    def get_history(self, dataset_id: str) -> List[DatasetRecord]:
        return [d for d in self._datasets.values() if d.dataset_id == dataset_id]
    @staticmethod
    def compute_hash(data: Any) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]
    def count(self) -> int: return len(self._datasets)
