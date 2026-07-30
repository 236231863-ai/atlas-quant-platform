"""Open API Platform - external API with auth, rate limiting, permissions."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class DeveloperAPIKey: id:str; user_id:str; key_hash:str; permissions:List[str]=field(default_factory=lambda:["basic"]); rate_limit:int=100; created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat()); def to_dict(self):return asdict(self)

class APIGateway:
    def __init__(self): self._keys: Dict[str, DeveloperAPIKey] = {}; self._usage: Dict[str, int] = {}
    def create_key(self, uid: str) -> DeveloperAPIKey:
        key = DeveloperAPIKey(id=str(uuid.uuid4()), user_id=uid, key_hash=str(uuid.uuid4())[:8])
        self._keys[key.id] = key; return key
    def validate_key(self, key_hash: str) -> bool:
        return any(k.key_hash == key_hash for k in self._keys.values())
    def check_permission(self, key_hash: str, permission: str) -> bool:
        key = next((k for k in self._keys.values() if k.key_hash == key_hash), None)
        return permission in key.permissions if key else False
    def check_rate_limit(self, key_hash: str) -> bool:
        self._usage[key_hash] = self._usage.get(key_hash, 0) + 1
        key = next((k for k in self._keys.values() if k.key_hash == key_hash), None)
        return self._usage[key_hash] <= key.rate_limit if key else False
    def list_keys(self, uid: str) -> List[DeveloperAPIKey]:
        return [k for k in self._keys.values() if k.user_id == uid]
    def count_keys(self) -> int: return len(self._keys)
