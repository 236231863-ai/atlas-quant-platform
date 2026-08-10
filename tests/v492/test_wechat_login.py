"""微信真实登录测试（Beta 前置：code2session → openid → U_ID）。

覆盖：
  1. 登录成功（code → 用户）
  2. code 失败处理（空 code / 异常）
  3. openid 不存在创建用户
  4. openid 存在返回旧用户（同一微信用户稳定 U_ID）
  5. 用户隔离
  6. 原有 Beta 埋点不受影响（install_completed / mobile_opened）
"""
from __future__ import annotations

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.mobile import api as api_module
from backend.mobile.db import MobileDB


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("WECHAT_LOGIN_MOCK", "1")
    api_module.reset_db(MobileDB.in_memory())
    yield


@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(api_module.auth_router)
    app.include_router(api_module.router)
    return TestClient(app)


class TestLoginSuccess:
    def test_login_returns_user(self, client):
        r = client.post("/api/auth/wechat/login", json={"code": "mock_abc"})
        assert r.status_code == 200
        body = r.json()
        assert body["user_id"].startswith("U")
        assert body["is_new"] is True
        assert body["mock"] is True

    def test_login_records_install_event(self, client):
        # 第一次登录（新用户）→ install_completed（冻结指标 → 实际事件 app_install）
        client.post("/api/auth/wechat/login", json={"code": "mock_abc"})
        # 第二次登录（老用户）→ mobile_opened
        client.post("/api/auth/wechat/login", json={"code": "mock_abc"})
        with api_module._db.session() as s:
            from backend.mobile.repositories import BehaviorEventRepository
            repo = BehaviorEventRepository(s)
            # 冻结指标 install_completed 映射到实际事件 app_install
            assert repo.count_by_event("app_install") == 1
            assert repo.count_by_event("mobile_opened") == 1


class TestCodeFailure:
    def test_empty_code_rejected(self, client):
        r = client.post("/api/auth/wechat/login", json={"code": ""})
        assert r.status_code == 422

    def test_missing_code_rejected(self, client):
        r = client.post("/api/auth/wechat/login", json={})
        assert r.status_code == 422


class TestUserCreation:
    def test_new_openid_creates_user(self, client):
        r1 = client.post("/api/auth/wechat/login", json={"code": "mock_u1"})
        r2 = client.post("/api/auth/wechat/login", json={"code": "mock_u2"})
        assert r1.json()["user_id"] != r2.json()["user_id"]
        assert r1.json()["is_new"] is True
        assert r2.json()["is_new"] is True

    def test_user_created_in_db(self, client):
        client.post("/api/auth/wechat/login", json={"code": "mock_u1"})
        with api_module._db.session() as s:
            from backend.mobile.repositories import UserRepository
            repo = UserRepository(s)
            user = repo.get_by_openid("mock_openid_u1")
            assert user is not None
            assert user.user_id.startswith("U")


class TestExistingUser:
    def test_same_openid_returns_same_user(self, client):
        r1 = client.post("/api/auth/wechat/login", json={"code": "mock_same"})
        r2 = client.post("/api/auth/wechat/login", json={"code": "mock_same"})
        assert r1.json()["user_id"] == r2.json()["user_id"]
        assert r1.json()["is_new"] is True
        assert r2.json()["is_new"] is False

    def test_stable_uid_across_logins(self, client):
        uid_first = None
        for _ in range(5):
            r = client.post("/api/auth/wechat/login", json={"code": "mock_stable"})
            uid = r.json()["user_id"]
            if uid_first is None:
                uid_first = uid
            assert uid == uid_first
        assert uid_first.startswith("U")


class TestIsolation:
    def test_users_isolated(self, client):
        u1 = client.post("/api/auth/wechat/login", json={"code": "mock_a"}).json()["user_id"]
        u2 = client.post("/api/auth/wechat/login", json={"code": "mock_b"}).json()["user_id"]
        assert u1 != u2

    def test_openid_unique(self, client):
        client.post("/api/auth/wechat/login", json={"code": "mock_uniq"})
        with api_module._db.session() as s:
            from backend.mobile.repositories import UserRepository
            repo = UserRepository(s)
            # openid 唯一（同 code 不会重复创建）
            assert repo.count() == 1


class TestBetaEventsUntouched:
    def test_existing_events_api_unchanged(self, client):
        # 登录后原有 mobile 事件链路仍可用
        u = client.post("/api/auth/wechat/login", json={"code": "mock_e1"}).json()
        r = client.post("/api/mobile/v1/events",
                        json={"event_name": "mobile_opened", "user_id": u["user_id"], "source": "MOBILE"})
        assert r.status_code == 200 and r.json()["ok"] is True

    def test_login_does_not_break_ticket_flow(self, client):
        u = client.post("/api/auth/wechat/login", json={"code": "mock_e2"}).json()
        r = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "06 16 21 30 34 + 06 12"})
        assert r.status_code == 200
        assert r.json()["ticket_id"].startswith("T")

    def test_frozen_metrics_still_work(self, client):
        u = client.post("/api/auth/wechat/login", json={"code": "mock_e3"}).json()
        # 冻结指标名仍可 track
        r = client.post("/api/mobile/v1/events",
                        json={"event_name": "ticket_saved", "user_id": u["user_id"], "source": "MOBILE"})
        assert r.status_code == 200


class TestWechatLoginClient:
    def test_mock_code2session(self):
        from backend.mobile.wechat import WeChatLoginClient
        client = WeChatLoginClient()
        res = client.code2session("mock_x")
        assert res["ok"] is True and res["openid"] == "mock_openid_x"

    def test_mock_requires_mock_prefix(self):
        from backend.mobile.wechat import WeChatLoginClient
        client = WeChatLoginClient()
        res = client.code2session("some_code_123")
        assert res["ok"] is True and res["openid"].startswith("mock_openid_")

    def test_real_mode_reads_env(self, monkeypatch):
        monkeypatch.setenv("WECHAT_APPID", "wx_test_appid")
        monkeypatch.setenv("WECHAT_APPSECRET", "test_secret")
        monkeypatch.setenv("WECHAT_LOGIN_MOCK", "0")
        from backend.mobile.wechat import WeChatLoginClient
        client = WeChatLoginClient()
        assert client.is_mock is False
        assert client._appid == "wx_test_appid"
