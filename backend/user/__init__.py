"""User Account System - register, login, profile, preferences."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class User:
    user_id: str; username: str; email: str; password_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    settings: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return asdict(self)

class UserService:
    def __init__(self):
        self._users: Dict[str, User] = {}
    def register(self, username: str, email: str, password: str) -> User:
        uid = str(uuid.uuid4())
        user = User(user_id=uid, username=username, email=email, password_hash=password)
        self._users[uid] = user; return user
    def login(self, username: str, password: str) -> Optional[User]:
        for u in self._users.values():
            if u.username == username and u.password_hash == password: return u
        return None
    def get_user(self, uid: str) -> Optional[User]: return self._users.get(uid)
    def update_profile(self, uid: str, email: str) -> bool:
        user = self._users.get(uid)
        if not user: return False
        user.email = email; return True
    def update_preferences(self, uid: str, settings: Dict[str, Any]) -> bool:
        user = self._users.get(uid)
        if not user: return False
        user.settings.update(settings); return True
    def list_users(self) -> List[User]: return list(self._users.values())
    def count(self) -> int: return len(self._users)
