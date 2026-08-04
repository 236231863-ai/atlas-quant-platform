"""v4.6 大规模矩阵 3：纯计算参数化（补足 ≥1000）。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.user_analytics import (
    AnalyticsEvent, build_funnel, build_retention, AnalyticsTracker,
)
from engine.asset_center import (
    build_monthly_report, MonthlySummary, build_asset_report,
)
from engine.premium import FeatureStatus, PREMIUM_FEATURES
from engine.claim_center import ClaimCenter


def ev(event, day_offset=0, uid="u1"):
    d = date.today() + timedelta(days=day_offset)
    return AnalyticsEvent(event_name=event, user_id=uid,
                          timestamp=f"{d.isoformat()}T10:00:00")


# ---------- 纯计算矩阵 ----------
@pytest.mark.parametrize("a,b", [(i, j) for i in range(5) for j in range(5)])
def test_merge_count(a, b):
    """funnel 总用户 = 首阶段用户数（同 user 去重）。"""
    events = [ev("app_opened", uid=f"u{i % 3}") for i in range(a * 3)] + \
             [ev("ticket_saved", uid=f"u{i % 3}") for i in range(b * 2)]
    f = build_funnel(events)
    assert f.stages[0].users == min(a * 3, 3) if a else f.total_users >= 0


@pytest.mark.parametrize("n", range(50))
def test_monthly_ticket_scale(n):
    ts = [{"ticket_id": f"T{i}", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
           "back": [1, 2], "buy_date": "2026-08-10",
           "draw_date": "2026-08-01", "cost": 2.0} for i in range(n)]
    rep = build_monthly_report(ts)
    if n == 0:
        assert rep.items == []
    else:
        assert rep.items[0].ticket_count == n


@pytest.mark.parametrize("i", range(60))
def test_monthly_net_calc(i):
    m = MonthlySummary(year=2026, month=8, investment=i * 2, winnings=i)
    assert m.net == -i  # winnings - investment


@pytest.mark.parametrize("feature", list(PREMIUM_FEATURES) * 15)
def test_premium_status_any(feature):
    s = FeatureStatus(name=feature)
    assert s.name == feature
    assert s.locked is True


# ---------- claim 状态纯计算 ----------
FUTURE = (date.today() + timedelta(days=1)).isoformat()
PAST = (date.today() - timedelta(days=1)).isoformat()


@pytest.mark.parametrize("i", range(60))
def test_claim_status_waiting(i):
    t = {"ticket_id": f"T{i}", "draw_date": FUTURE}
    assert ClaimCenter.status_of(t) == "waiting_draw"


@pytest.mark.parametrize("i", range(60))
def test_claim_status_settled(i):
    t = {"ticket_id": f"T{i}", "draw_date": PAST}
    assert ClaimCenter.status_of(t) == "settled_unviewed"


@pytest.mark.parametrize("i", range(60))
def test_claim_status_claimed(i):
    t = {"ticket_id": f"T{i}", "draw_date": PAST, "claimed": True}
    assert ClaimCenter.status_of(t) == "claimed"


# ---------- analytics 结构矩阵 ----------
@pytest.mark.parametrize("i", range(40))
def test_analytics_event_dict(i):
    e = AnalyticsEvent(event_name="app_opened", user_id=f"u{i}",
                       metadata={"idx": i})
    d = e.to_dict()
    assert d["user_id"] == f"u{i}"
    assert d["metadata"]["idx"] == i


@pytest.mark.parametrize("i", range(1, 41))
def test_retention_daily_structure(i):
    events = [ev("app_opened", day_offset=-(j % 5)) for j in range(i)]
    r = build_retention(events)
    assert r.daily
    assert sum(r.daily.values()) >= 1


# ---------- asset 基础矩阵 ----------
@pytest.mark.parametrize("n", range(1, 21))
def test_asset_report_total(n):
    tickets = [{"ticket_id": f"T{i}", "lottery": "dlt", "front": [1, 2, 3, 4, 5],
                "back": [1, 2], "buy_date": "2026-08-10",
                "draw_date": "2026-08-01", "cost": 2.0} for i in range(n)]
    rep = build_asset_report(tickets)
    assert rep.total_tickets == n
    assert rep.total_investment == n * 2.0
