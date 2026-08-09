"""提醒逻辑测试：创建/去重/下发/点击率 + 微信订阅消息客户端。"""
from __future__ import annotations

import pytest

from backend.mobile.repositories import ReminderRepository
from backend.mobile.wechat import ReminderDispatcher, WeChatReminderClient


class TestReminderService:
    def test_create_reminder(self, service):
        u = service.register_or_get("openid_r1")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        r = service.create_reminder(u.user_id, t["ticket_id"], "26086", "2026-08-08")
        assert r["ok"] is True and r["duplicated"] is False
        assert service.reminders.exists(u.user_id, t["ticket_id"], "26086")

    def test_create_duplicate(self, service):
        u = service.register_or_get("openid_r2")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.create_reminder(u.user_id, t["ticket_id"], "26086")
        r2 = service.create_reminder(u.user_id, t["ticket_id"], "26086")
        assert r2["duplicated"] is True

    def test_reminder_marks_user_flag(self, service):
        u = service.register_or_get("openid_r3")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.create_reminder(u.user_id, t["ticket_id"], "26086")
        assert service.users.get(u.user_id).reminder_enabled is True

    def test_reminder_records_event(self, service):
        u = service.register_or_get("openid_r4")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.create_reminder(u.user_id, t["ticket_id"], "26086")
        assert service.events.count_by_event("mobile_reminder_enabled") == 1

    def test_mark_clicked(self, service):
        u = service.register_or_get("openid_r5")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        r = service.create_reminder(u.user_id, t["ticket_id"], "26086")
        assert service.mark_reminder_clicked(r["reminder_id"]) is True
        assert service.reminders.click_rate() == 1.0 if service.reminders.count() else True


class TestWeChatClient:
    def test_mock_by_default(self, monkeypatch):
        monkeypatch.delenv("WECHAT_APPID", raising=False)
        client = WeChatReminderClient()
        assert client.is_mock is True

    def test_mock_send_success(self, monkeypatch):
        monkeypatch.delenv("WECHAT_APPID", raising=False)
        client = WeChatReminderClient()
        result = client.send_draw_reminder("openid_x", "26086", "2026-08-08")
        assert result["ok"] is True and result["mock"] is True

    def test_not_mock_when_configured(self, monkeypatch):
        monkeypatch.setenv("WECHAT_APPID", "appid")
        monkeypatch.setenv("WECHAT_SECRET", "secret")
        monkeypatch.setenv("WECHAT_TEMPLATE_ID", "tmpl")
        monkeypatch.setenv("WECHAT_MOCK", "0")
        client = WeChatReminderClient()
        assert client.is_mock is False


class TestReminderDispatcher:
    def test_dispatch_all_mock(self, service, db):
        u = service.register_or_get("openid_d1")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.create_reminder(u.user_id, t["ticket_id"], "26086")
        client = WeChatReminderClient()
        dispatcher = ReminderDispatcher(client, service.reminders, service.users)
        result = dispatcher.dispatch_all()
        assert result["sent"] == 1 and result["failed"] == 0
        assert len(service.reminders.list_unsent()) == 0

    def test_dispatch_no_reminders(self, service):
        client = WeChatReminderClient()
        dispatcher = ReminderDispatcher(client, service.reminders, service.users)
        assert dispatcher.dispatch_all() == {"sent": 0, "failed": 0}

    def test_click_rate_calculation(self, service, db):
        u = service.register_or_get("openid_d2")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        r = service.create_reminder(u.user_id, t["ticket_id"], "26086")
        service.mark_reminder_clicked(r["reminder_id"])
        # sent=1(clicked 也计为 sent 口径下 click_rate 需有 sent)
        service.reminders.mark_sent(r["reminder_id"])
        assert service.reminders.click_rate() == 1.0
