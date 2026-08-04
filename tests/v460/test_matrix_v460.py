"""v4.6 大规模矩阵 1：analytics/funnel/retention/premium/monthly。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.user_analytics import (
    EVENT_NAMES, AnalyticsEvent, AnalyticsTracker, build_funnel, build_retention,
)
from engine.premium import PREMIUM_FEATURES, PremiumFeatureTest, FeatureStatus
from engine.asset_center import build_monthly_report


def ev(event, day_offset=0, uid="u1", hour=10):
    d = date.today() + timedelta(days=day_offset)
    return AnalyticsEvent(event_name=event, user_id=uid,
                          timestamp=f"{d.isoformat()}T{hour:02d}:00:00",
                          source="desktop", metadata={})


# ---------- analytics 事件矩阵 ----------
@pytest.mark.parametrize("event", list(EVENT_NAMES) * 5)
def test_analytics_event_all(ticket_storage, event):
    AnalyticsTracker().clear()
    AnalyticsTracker().record(event)
    assert AnalyticsTracker().count(event) == 1


@pytest.mark.parametrize("n", range(30))
def test_analytics_count_scale(ticket_storage, n):
    AnalyticsTracker().clear()
    for _ in range(n):
        AnalyticsTracker().record("app_opened")
    assert AnalyticsTracker().count("app_opened") == n


# ---------- funnel 矩阵 ----------
@pytest.mark.parametrize("n_users", range(1, 11))
def test_funnel_users(n_users):
    events = [ev("app_opened", uid=f"u{i}") for i in range(n_users)]
    f = build_funnel(events)
    assert f.total_users == n_users
    assert f.stages[0].users == n_users


@pytest.mark.parametrize("n_save", range(0, 11))
def test_funnel_save_drop(n_save):
    events = [ev("app_opened", uid=f"u{i}") for i in range(10)] + \
             [ev("ticket_saved", uid=f"u{i}") for i in range(n_save)]
    f = build_funnel(events)
    assert f.stages[1].users == n_save
    assert f.stages[1].conversion == pytest.approx(n_save / 10)


@pytest.mark.parametrize("seed", range(20))
def test_funnel_random(seed):
    import random
    random.seed(seed)
    events = []
    for i in range(random.randint(5, 25)):
        uid = f"u{random.randint(0, 7)}"
        stage = random.choice(["app_opened", "ticket_saved", "ticket_checked",
                               "claim_completed", "report_viewed"])
        events.append(ev(stage, uid=uid))
    f = build_funnel(events)
    assert f.to_dict()


# ---------- retention 矩阵 ----------
@pytest.mark.parametrize("offset", range(-1, -15, -1))
def test_retention_offsets(offset):
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=offset)]
    r = build_retention(events)
    assert r.active_days >= 2


@pytest.mark.parametrize("seed", range(25))
def test_retention_random(seed):
    import random
    random.seed(seed)
    events = []
    for i in range(random.randint(5, 40)):
        events.append(ev("app_opened", day_offset=-random.randint(0, 10),
                         uid=f"u{random.randint(0, 4)}"))
    r = build_retention(events)
    assert r.active_days >= 1
    assert 0.0 <= r.d1 <= 1.0
    assert 0.0 <= r.d3 <= 1.0
    assert 0.0 <= r.d7 <= 1.0


# ---------- premium 矩阵 ----------
@pytest.mark.parametrize("feature", list(PREMIUM_FEATURES) * 10)
def test_premium_feature_locked(feature):
    s = PremiumFeatureTest.feature_status(feature)
    assert s.locked is True
    assert "解锁" in s.unlock_text


@pytest.mark.parametrize("i", range(30))
def test_premium_view_click(ticket_storage, i):
    AnalyticsTracker().clear()
    f = PREMIUM_FEATURES[i % 4]
    PremiumFeatureTest.view(f)
    PremiumFeatureTest.click(f)
    s = AnalyticsTracker().summary()
    assert s["premium_view"] == 1
    assert s["premium_click"] == 1


@pytest.mark.parametrize("locked", [True, False] * 10)
def test_feature_status_variants(locked):
    s = FeatureStatus(name="测试", locked=locked)
    assert s.locked is locked
    if locked:
        assert s.unlock_text
    else:
        assert s.unlock_text == ""


# ---------- monthly 矩阵 ----------
@pytest.mark.parametrize("month", range(1, 13))
def test_monthly_single(month):
    t = {"ticket_id": "T", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
         "back": [1, 2], "buy_date": f"2026-{month:02d}-10",
         "draw_date": "2026-08-01", "cost": 2.0}
    rep = build_monthly_report([t])
    assert rep.items[0].month == month
    assert rep.items[0].investment == 2.0


@pytest.mark.parametrize("cost", [0, 1, 2, 5, 10, 20, 50])
def test_monthly_cost(cost):
    t = {"ticket_id": "T", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
         "back": [1, 2], "buy_date": "2026-08-10",
         "draw_date": "2026-08-01", "cost": cost}
    rep = build_monthly_report([t])
    assert rep.items[0].investment == cost


@pytest.mark.parametrize("n", range(1, 16))
def test_monthly_tickets(n):
    ts = [{"ticket_id": f"T{i}", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
           "back": [1, 2], "buy_date": "2026-08-10",
           "draw_date": "2026-08-01", "cost": 2.0} for i in range(n)]
    rep = build_monthly_report(ts)
    assert rep.items[0].ticket_count == n
    assert rep.items[0].investment == n * 2.0


# ---------- 综合矩阵 ----------
@pytest.mark.parametrize("i", range(20))
def test_combined_stable(ticket_storage, i):
    AnalyticsTracker().clear()
    for j in range(5):
        AnalyticsTracker().record("app_opened")
        AnalyticsTracker().record("ticket_saved")
    f = build_funnel()
    r = build_retention()
    assert f.to_dict()
    assert r.to_dict()
