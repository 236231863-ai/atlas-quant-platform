"""User workspace models and service."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class UserData:
    username: str; email: str; role: str = "researcher"; id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self):
        return asdict(self)

@dataclass
class WorkspaceData:
    name: str; user_id: str; description: str = ""; id: Optional[str] = None
    def to_dict(self):
        return asdict(self)

@dataclass
class ProjectData:
    name: str; workspace_id: str; lottery_code: str = "dlt"; description: str = ""; id: Optional[str] = None
    def to_dict(self):
        return asdict(self)

class UserService:
    def __init__(self):
        self._users: Dict[str, UserData] = {}
        self._workspaces: Dict[str, WorkspaceData] = {}
        self._projects: Dict[str, ProjectData] = {}
    def create_user(self, user: UserData) -> UserData: import uuid; user.id = str(uuid.uuid4()); self._users[user.id] = user; return user
    def get_user(self, uid: str) -> Optional[UserData]: return self._users.get(uid)
    def list_users(self) -> List[UserData]: return list(self._users.values())
    def create_workspace(self, ws: WorkspaceData) -> WorkspaceData: import uuid; ws.id = str(uuid.uuid4()); self._workspaces[ws.id] = ws; return ws
    def list_workspaces(self, user_id: str) -> List[WorkspaceData]: return [w for w in self._workspaces.values() if w.user_id == user_id]
    def create_project(self, proj: ProjectData) -> ProjectData: import uuid; proj.id = str(uuid.uuid4()); self._projects[proj.id] = proj; return proj
    def list_projects(self, workspace_id: str) -> List[ProjectData]: return [p for p in self._projects.values() if p.workspace_id == workspace_id]
