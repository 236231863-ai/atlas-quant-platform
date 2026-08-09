"""Repository 层测试：五张表增删查 + 编号分配 + 去重。"""
from __future__ import annotations

import pytest

from backend.mobile.repositories import (
    BehaviorEventRepository,
    DrawRepository,
    ReminderRepository,
    TicketRepository,
    UserRepository,
)


@pytest.fixture
def session(db):
    return db.session()


class TestUserRepository:
    def test_create_and_get(self, session):
        repo = UserRepository(session)
        u = repo.create("openid_a", "大乐透", "每周")
        assert u.user_id == "U0001"
        assert repo.get("U0001").openid == "openid_a"

    def test_get_by_openid(self, session):
        repo = UserRepository(session)
        repo.create("openid_b")
        assert repo.get_by_openid("openid_b").user_id == "U0001"
        assert repo.get_by_openid("nonexistent") is None

    def test_next_user_id_increment(self, session):
        repo = UserRepository(session)
        repo.create("o1")
        repo.create("o2")
        assert repo.next_user_id() == "U0003"

    def test_count(self, session):
        repo = UserRepository(session)
        assert repo.count() == 0
        repo.create("o1")
        repo.create("o2")
        assert repo.count() == 2

    def test_mark_field(self, session):
        repo = UserRepository(session)
        u = repo.create("o1")
        assert repo.mark(u.user_id, "reminder_enabled") is True
        assert repo.get(u.user_id).reminder_enabled is True

    def test_mark_invalid_field(self, session):
        repo = UserRepository(session)
        u = repo.create("o1")
        assert repo.mark(u.user_id, "bogus") is False

    def test_mark_missing_user(self, session):
        repo = UserRepository(session)
        assert repo.mark("U9999", "draw_checked") is False

    def test_set_first_ticket(self, session):
        repo = UserRepository(session)
        u = repo.create("o1")
        assert repo.set_first_ticket_at(u.user_id, "2026-08-10T10:00:00") is True
        assert repo.get(u.user_id).first_ticket_saved_at == "2026-08-10T10:00:00"


class TestTicketRepository:
    def test_create_and_list(self, session):
        repo = TicketRepository(session)
        repo.create("U0001", "dlt", [1, 2, 3, 4, 5], [6, 12])
        repo.create("U0001", "dlt", [7, 8, 9, 10, 11], [1, 2])
        repo.create("U0002", "ssq", [1, 2, 3, 4, 5, 6], [7])
        assert len(repo.list_by_user("U0001")) == 2
        assert len(repo.list_by_user("U0002")) == 1

    def test_next_ticket_id(self, session):
        repo = TicketRepository(session)
        assert repo.next_ticket_id() == "T0001"
        repo.create("U0001", "dlt", [1, 2, 3, 4, 5], [6, 12])
        assert repo.next_ticket_id() == "T0002"

    def test_delete(self, session):
        repo = TicketRepository(session)
        t = repo.create("U0001", "dlt", [1, 2, 3, 4, 5], [6, 12])
        assert repo.delete(t.ticket_id) is True
        assert repo.list_by_user("U0001") == []

    def test_get(self, session):
        repo = TicketRepository(session)
        t = repo.create("U0001", "dlt", [1, 2, 3, 4, 5], [6, 12])
        assert repo.get(t.ticket_id) is not None
        assert repo.get("T9999") is None

    def test_list_by_issue(self, session):
        repo = TicketRepository(session)
        repo.create("U0001", "dlt", [1, 2, 3, 4, 5], [6, 12], issue="26086")
        repo.create("U0001", "dlt", [7, 8, 9, 10, 11], [1, 2], issue="26086")
        assert len(repo.list_by_issue("26086")) == 2
        assert len(repo.list_by_issue("26087")) == 0


class TestDrawRepository:
    def test_upsert_new(self, session):
        repo = DrawRepository(session)
        d = repo.upsert("26086", "dlt", [1, 2, 3, 4, 5], [6, 12], "2026-08-01")
        assert repo.get("26086").front == [1, 2, 3, 4, 5]

    def test_upsert_existing(self, session):
        repo = DrawRepository(session)
        repo.upsert("26086", "dlt", [1, 2, 3, 4, 5], [6, 12], "2026-08-01")
        repo.upsert("26086", "dlt", [9, 9, 9, 9, 9], [9, 9], "2026-08-01")
        assert repo.get("26086").front == [9, 9, 9, 9, 9]

    def test_latest(self, session):
        repo = DrawRepository(session)
        repo.upsert("26085", "dlt", [1, 2, 3, 4, 5], [6, 12])
        repo.upsert("26086", "dlt", [7, 8, 9, 10, 11], [1, 2])
        assert repo.latest("dlt").issue == "26086"

    def test_list_recent_order(self, session):
        repo = DrawRepository(session)
        repo.upsert("26085", "dlt", [1, 2, 3, 4, 5], [6, 12])
        repo.upsert("26086", "dlt", [7, 8, 9, 10, 11], [1, 2])
        recent = repo.list_recent("dlt", 2)
        assert recent[0].issue == "26086"

    def test_count(self, session):
        repo = DrawRepository(session)
        repo.upsert("26085", "dlt", [1, 2, 3, 4, 5], [6, 12])
        repo.upsert("26086", "dlt", [7, 8, 9, 10, 11], [1, 2])
        assert repo.count() == 2


class TestReminderRepository:
    def test_create_and_exists(self, session):
        repo = ReminderRepository(session)
        r = repo.create("U0001", "T0001", "26086", "2026-08-08")
        assert repo.exists("U0001", "T0001", "26086") is True
        assert repo.exists("U0001", "T0001", "26087") is False

    def test_mark_sent_and_clicked(self, session):
        repo = ReminderRepository(session)
        r = repo.create("U0001", "T0001", "26086")
        assert repo.mark_sent(r.id) is True
        assert repo.mark_clicked(r.id) is True
        assert len(repo.list_unsent()) == 0

    def test_click_rate(self, session):
        repo = ReminderRepository(session)
        assert repo.click_rate() == 0.0
        r1 = repo.create("U0001", "T0001", "26086")
        r2 = repo.create("U0001", "T0002", "26086")
        repo.mark_sent(r1.id)
        repo.mark_sent(r2.id)
        repo.mark_clicked(r1.id)
        assert repo.click_rate() == 0.5

    def test_count(self, session):
        repo = ReminderRepository(session)
        repo.create("U0001", "T0001", "26086")
        repo.create("U0001", "T0002", "26086")
        assert repo.count() == 2


class TestEventRepository:
    def test_record_and_count(self, session):
        repo = BehaviorEventRepository(session)
        repo.record("mobile_opened", "U0001", "MOBILE", {"page": "onboarding"})
        assert repo.count() == 1
        assert repo.count_by_event("mobile_opened") == 1

    def test_list_by_user(self, session):
        repo = BehaviorEventRepository(session)
        repo.record("app_open", "U0001", "MOBILE")
        repo.record("mobile_ticket_saved", "U0001", "MOBILE")
        repo.record("app_open", "U0002", "MOBILE")
        assert len(repo.list_by_user("U0001")) == 2

    def test_list_by_source(self, session):
        repo = BehaviorEventRepository(session)
        repo.record("mobile_opened", "U0001", "MOBILE")
        repo.record("mobile_opened", "U0001", "SIMULATION")
        assert len(repo.list_by_source("MOBILE")) == 1
        assert len(repo.list_by_source("SIMULATION")) == 1

    def test_data_column_stores_metadata(self, session):
        repo = BehaviorEventRepository(session)
        evt = repo.record("mobile_feedback_submitted", "U0001", "MOBILE",
                          metadata={"q1": "A"})
        assert evt.data == {"q1": "A"}
