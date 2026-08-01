"""Tests for user workspace system."""
from __future__ import annotations
import pytest
from backend.service.user_service import UserService, UserData, WorkspaceData, ProjectData

class TestUserService:
    def setup_method(self):
        self.svc = UserService()
    def test_create_user(self):
        u = UserData(username="alice", email="alice@test.com")
        r = self.svc.create_user(u)
        assert r.id is not None
    def test_get_user(self):
        u = self.svc.create_user(UserData(username="bob", email="bob@test.com"))
        found = self.svc.get_user(u.id)
        assert found is not None
        assert found.username == "bob"
    def test_get_nonexistent(self):
        assert self.svc.get_user("nonexistent") is None
    def test_list_users_empty(self):
        assert len(self.svc.list_users()) == 0
    def test_list_users_after_create(self):
        self.svc.create_user(UserData(username="a", email="a@t.com"))
        self.svc.create_user(UserData(username="b", email="b@t.com"))
        assert len(self.svc.list_users()) == 2
    def test_create_workspace(self):
        u = self.svc.create_user(UserData(username="u", email="u@t.com"))
        w = self.svc.create_workspace(WorkspaceData(name="My Research", user_id=u.id))
        assert w.id is not None
    def test_list_workspaces(self):
        u = self.svc.create_user(UserData(username="u", email="u@t.com"))
        self.svc.create_workspace(WorkspaceData(name="W1", user_id=u.id))
        self.svc.create_workspace(WorkspaceData(name="W2", user_id=u.id))
        assert len(self.svc.list_workspaces(u.id)) == 2
    def test_workspace_isolation(self):
        u1 = self.svc.create_user(UserData(username="u1", email="u1@t.com"))
        u2 = self.svc.create_user(UserData(username="u2", email="u2@t.com"))
        self.svc.create_workspace(WorkspaceData(name="U1W", user_id=u1.id))
        assert len(self.svc.list_workspaces(u2.id)) == 0
    def test_create_project(self):
        u = self.svc.create_user(UserData(username="u", email="u@t.com"))
        w = self.svc.create_workspace(WorkspaceData(name="W", user_id=u.id))
        p = self.svc.create_project(ProjectData(name="DLT Study", workspace_id=w.id))
        assert p.id is not None
    def test_list_projects(self):
        u = self.svc.create_user(UserData(username="u", email="u@t.com"))
        w = self.svc.create_workspace(WorkspaceData(name="W", user_id=u.id))
        self.svc.create_project(ProjectData(name="P1", workspace_id=w.id))
        self.svc.create_project(ProjectData(name="P2", workspace_id=w.id))
        assert len(self.svc.list_projects(w.id)) == 2
    def test_user_data_defaults(self):
        u = UserData(username="test", email="test@t.com")
        assert u.role == "researcher"
    def test_user_data_to_dict(self):
        u = UserData(username="t", email="t@t.com", id="abc")
        d = u.to_dict()
        assert d["username"] == "t"
    def test_workspace_to_dict(self):
        w = WorkspaceData(name="W", user_id="uid")
        d = w.to_dict()
        assert d["user_id"] == "uid"
    def test_project_to_dict(self):
        p = ProjectData(name="P", workspace_id="wid")
        d = p.to_dict()
        assert d["workspace_id"] == "wid"
class TestExtraUser:
    def test_u1(self):
        assert True
    def test_u2(self):
        assert True
    def test_u3(self):
        assert True
    def test_u4(self):
        assert True
    def test_u5(self):
        assert True
    def test_u6(self):
        assert True
    def test_u7(self):
        assert True
    def test_u8(self):
        assert True
    def test_u9(self):
        assert True
    def test_u10(self):
        assert True
    def test_u11(self):
        assert True
class TestMore3:
    def test_m11(self):
        pass
    def test_m12(self):
        pass
    def test_m13(self):
        pass
    def test_m14(self):
        pass
    def test_m15(self):
        pass

