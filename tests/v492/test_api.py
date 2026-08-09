"""FastAPI 路由测试（/api/mobile/v1）。

隔离：每个测试前将 api._db 替换为 in-memory MobileDB，不触碰真实存储。
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.mobile import api as api_module
from backend.mobile.db import MobileDB
from backend.mobile.repositories import DrawRepository


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    api_module.reset_db(MobileDB.in_memory())
    yield


@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(api_module.router)
    return TestClient(app)


def _seed_draw(issue="26086", lottery="dlt", front=(10, 11, 18, 22, 35), back=(6, 12)):
    """用 Repository 直接写入一期开奖（不走 HTTP）。"""
    with api_module._db.session() as s:
        DrawRepository(s).upsert(issue, lottery, list(front), list(back), "2026-08-01")


class TestAuthAPI:
    def test_auth_new_user(self, client):
        r = client.post("/api/mobile/v1/users/auth",
                        json={"openid": "api_o1", "lottery_type": "大乐透", "purchase_frequency": "每周"})
        assert r.status_code == 200
        assert r.json()["user_id"].startswith("U")

    def test_auth_dedup(self, client):
        r1 = client.post("/api/mobile/v1/users/auth", json={"openid": "api_o2"})
        r2 = client.post("/api/mobile/v1/users/auth", json={"openid": "api_o2"})
        assert r1.json()["user_id"] == r2.json()["user_id"]

    def test_auth_missing_openid(self, client):
        r = client.post("/api/mobile/v1/users/auth", json={})
        assert r.status_code == 422


class TestTicketAPI:
    def _auth(self, client, openid="api_t1"):
        return client.post("/api/mobile/v1/users/auth", json={"openid": openid}).json()

    def test_create_ticket(self, client):
        u = self._auth(client)
        r = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "06 16 21 30 34 + 06 12"})
        assert r.status_code == 200
        assert r.json()["ticket_id"].startswith("T")

    def test_create_ticket_invalid(self, client):
        u = self._auth(client)
        r = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "99 100 101 102 103 + 99 99"})
        assert r.status_code == 422

    def test_list_tickets(self, client):
        u = self._auth(client)
        client.post("/api/mobile/v1/tickets",
                    json={"user_id": u["user_id"], "lottery": "dlt", "text": "01 02 03 04 05 + 01 02"})
        r = client.get(f"/api/mobile/v1/tickets?user_id={u['user_id']}")
        assert r.status_code == 200 and len(r.json()) == 1


class TestDrawAPI:
    def _auth(self, client):
        return client.post("/api/mobile/v1/users/auth", json={"openid": "api_d1"}).json()

    def test_latest_draw_after_seed(self, client):
        _seed_draw()
        r = client.get("/api/mobile/v1/draws/latest?lottery=dlt")
        assert r.status_code == 200
        assert r.json()["issue"] == "26086"

    def test_latest_draw_not_found(self, client):
        r = client.get("/api/mobile/v1/draws/latest?lottery=ssq")
        assert r.status_code == 404

    def test_check_draw_wins(self, client):
        u = self._auth(client)
        t = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "06 16 21 30 34 + 06 12"}).json()
        _seed_draw()
        r = client.post("/api/mobile/v1/draws/check",
                        json={"user_id": u["user_id"], "ticket_id": t["ticket_id"], "issue": "26086"})
        assert r.status_code == 200
        assert r.json()["result"]["won"] is True

    def test_check_draw_missing_ticket(self, client):
        u = self._auth(client)
        _seed_draw()
        r = client.post("/api/mobile/v1/draws/check",
                        json={"user_id": u["user_id"], "ticket_id": "T9999", "issue": "26086"})
        assert r.status_code == 404


class TestReminderAPI:
    def test_create_reminder(self, client):
        u = client.post("/api/mobile/v1/users/auth", json={"openid": "api_r1"}).json()
        t = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "01 02 03 04 05 + 01 02"}).json()
        r = client.post("/api/mobile/v1/reminders",
                        json={"user_id": u["user_id"], "ticket_id": t["ticket_id"],
                              "issue": "26086", "remind_at": "2026-08-08"})
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_reminder_click(self, client):
        u = client.post("/api/mobile/v1/users/auth", json={"openid": "api_r2"}).json()
        t = client.post("/api/mobile/v1/tickets",
                        json={"user_id": u["user_id"], "lottery": "dlt", "text": "01 02 03 04 05 + 01 02"}).json()
        rm = client.post("/api/mobile/v1/reminders",
                         json={"user_id": u["user_id"], "ticket_id": t["ticket_id"], "issue": "26086"}).json()
        r = client.post("/api/mobile/v1/reminders/click", json={"reminder_id": rm["reminder_id"]})
        assert r.status_code == 200 and r.json()["ok"] is True


class TestEventAPI:
    def test_track_event(self, client):
        u = client.post("/api/mobile/v1/users/auth", json={"openid": "api_e1"}).json()
        r = client.post("/api/mobile/v1/events",
                        json={"event_name": "mobile_opened", "user_id": u["user_id"], "source": "MOBILE"})
        assert r.status_code == 200 and r.json()["ok"] is True

    def test_track_unknown_event(self, client):
        u = client.post("/api/mobile/v1/users/auth", json={"openid": "api_e2"}).json()
        r = client.post("/api/mobile/v1/events",
                        json={"event_name": "bogus", "user_id": u["user_id"], "source": "MOBILE"})
        assert r.status_code == 422


class TestFunnelAPI:
    def test_funnel_empty(self, client):
        r = client.get("/api/mobile/v1/funnel")
        assert r.status_code == 200
        assert r.json() == {
            "registered": 0, "first_ticket_saved": 0,
            "reminder_enabled": 0, "draw_checked": 0,
        }
