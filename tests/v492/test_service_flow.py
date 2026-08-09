"""服务链路（页面流程）测试：注册 → 录票 → 提醒 → 查奖 → 漏斗。"""
from __future__ import annotations

import pytest

from backend.mobile.service import (
    EVENT_MOBILE_DRAW_VIEWED,
    EVENT_MOBILE_TICKET_SAVED,
    MobileService,
)


class TestAuthFlow:
    def test_register_new_user(self, service):
        u = service.register_or_get("openid_f1")
        assert u.user_id == "U0001"
        assert u.lottery_type == "大乐透"

    def test_auth_dedup(self, service):
        u1 = service.register_or_get("openid_f2")
        u2 = service.register_or_get("openid_f2")
        assert u1.user_id == u2.user_id

    def test_sequential_ids(self, service):
        a = service.register_or_get("o1")
        b = service.register_or_get("o2")
        assert a.user_id == "U0001" and b.user_id == "U0002"

    def test_unknown_frequency_normalized(self, service):
        u = service.register_or_get("o3", purchase_frequency="每天一百次")
        assert u.purchase_frequency == "首次"


class TestTicketFlow:
    def test_save_ticket_success(self, service):
        u = service.register_or_get("o_t1")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        assert t["ticket_id"].startswith("T")

    def test_save_invalid_rejected(self, service):
        u = service.register_or_get("o_t2")
        with pytest.raises(ValueError):
            service.save_ticket(u.user_id, "dlt", "99 100 101 102 103 + 01 02")

    def test_save_sets_first_ticket_milestone(self, service):
        u = service.register_or_get("o_t3")
        assert not u.first_ticket_saved_at
        service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        assert service.users.get(u.user_id).first_ticket_saved_at

    def test_save_records_event(self, service):
        u = service.register_or_get("o_t4")
        service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        assert service.events.count_by_event(EVENT_MOBILE_TICKET_SAVED) == 1

    def test_list_tickets(self, service):
        u = service.register_or_get("o_t5")
        service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.save_ticket(u.user_id, "dlt", "01 02 03 04 05 + 01 02")
        assert len(service.list_tickets(u.user_id)) == 2


class TestDrawCheckFlow:
    def _setup_user_with_draw(self, service):
        u = service.register_or_get("o_d1")
        t = service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        service.draws.upsert("26086", "dlt", [10, 11, 18, 22, 35], [6, 12], "2026-08-01")
        return u, t

    def test_check_wins(self, service):
        u, t = self._setup_user_with_draw(service)
        r = service.check_ticket(u.user_id, t["ticket_id"], "26086")
        assert r["ok"] and r["result"]["won"] and r["result"]["amount"] == 5.0

    def test_check_records_draw_viewed_event(self, service):
        u, t = self._setup_user_with_draw(service)
        service.check_ticket(u.user_id, t["ticket_id"], "26086")
        assert service.events.count_by_event(EVENT_MOBILE_DRAW_VIEWED) == 1

    def test_check_unknown_ticket(self, service):
        u, _ = self._setup_user_with_draw(service)
        r = service.check_ticket(u.user_id, "T9999", "26086")
        assert r["ok"] is False and r["reason"] == "not_found"

    def test_check_draw_not_found(self, service):
        u, t = self._setup_user_with_draw(service)
        r = service.check_ticket(u.user_id, t["ticket_id"], "26099")
        assert r["ok"] is False and r["reason"] == "draw_not_found"

    def test_latest_draw(self, service):
        service.draws.upsert("26086", "dlt", [10, 11, 18, 22, 35], [6, 12])
        draw = service.latest_draw("dlt")
        assert draw["issue"] == "26086"

    def test_latest_draw_empty(self, service):
        assert service.latest_draw("dlt") is None


class TestFunnelService:
    def test_empty_funnel(self, service):
        assert service.funnel() == {
            "registered": 0, "first_ticket_saved": 0,
            "reminder_enabled": 0, "draw_checked": 0,
        }

    def test_save_rate(self, service):
        u = service.register_or_get("o_f1")
        service.register_or_get("o_f2")
        service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        assert service.save_rate() == 0.5

    def test_funnel_counts(self, service):
        u = service.register_or_get("o_f3")
        service.save_ticket(u.user_id, "dlt", "06 16 21 30 34 + 06 12")
        t = service.list_tickets(u.user_id)[0]
        service.create_reminder(u.user_id, t["ticket_id"], "26086")
        service.draws.upsert("26086", "dlt", [10, 11, 18, 22, 35], [6, 12])
        service.check_ticket(u.user_id, t["ticket_id"], "26086")
        f = service.funnel()
        assert f["registered"] == 1
        assert f["first_ticket_saved"] == 1
        assert f["reminder_enabled"] == 1


class TestTrack:
    def test_track_valid_event(self, service):
        u = service.register_or_get("o_tk1")
        assert service.track("mobile_opened", u.user_id, "MOBILE") is True

    def test_track_unknown_event(self, service):
        u = service.register_or_get("o_tk2")
        assert service.track("bogus_event", u.user_id, "MOBILE") is False

    def test_track_legacy_event(self, service):
        u = service.register_or_get("o_tk3")
        assert service.track("app_open", u.user_id, "MOBILE") is True

    def test_track_simulation_allowed(self, service):
        u = service.register_or_get("o_tk4")
        assert service.track("mobile_opened", u.user_id, "SIMULATION") is True

    def test_all_mobile_events_trackable(self, service):
        u = service.register_or_get("o_tk5")
        for evt in ("mobile_opened", "mobile_ticket_saved", "mobile_reminder_enabled",
                    "mobile_draw_viewed", "mobile_feedback_submitted"):
            assert service.track(evt, u.user_id, "MOBILE") is True
