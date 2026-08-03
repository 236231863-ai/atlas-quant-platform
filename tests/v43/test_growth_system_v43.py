"""v4.3 P4：用户成长系统测试（≥100 场景）。

覆盖：成长指标 / 连续周数 / 等级 / 年度 Atlas Report / 事件集成。
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from engine.growth_system import (
    DISCLAIMER, AnnualGrowth, GrowthEngine, GrowthReport, build_growth,
)
from engine.user_events import EventTracker, UserEvent


def ev(event_type, day_offset=0, hour=10):
    """构造指定日偏移的事件。"""
    d = date.today() + timedelta(days=day_offset)
    return UserEvent(event_type=event_type,
                     created_at=f"{d.isoformat()}T{hour:02d}:00:00")


# ---------- 空数据 ----------
def test_empty_growth(ticket_storage):
    rep = GrowthEngine.build([])
    assert rep.tickets_saved == 0
    assert rep.claims_completed == 0
    assert rep.reports_viewed == 0
    assert rep.streak_weeks == 0
    assert rep.level == "见习"


def test_empty_events_from_tracker(ticket_storage):
    EventTracker().clear()
    rep = GrowthEngine.build()
    assert rep.total_events == 0


# ---------- 指标统计 ----------
def test_count_saved(ticket_storage):
    events = [ev("ticket_saved") for _ in range(5)]
    rep = GrowthEngine.build(events)
    assert rep.tickets_saved == 5


def test_count_claims(ticket_storage):
    events = [ev("claim_confirmed") for _ in range(3)]
    rep = GrowthEngine.build(events)
    assert rep.claims_completed == 3


def test_count_reports(ticket_storage):
    events = [ev("report_generated") for _ in range(4)]
    rep = GrowthEngine.build(events)
    assert rep.reports_viewed == 4


@pytest.mark.parametrize("n", [0, 1, 5, 10, 20])
def test_count_matrix(ticket_storage, n):
    events = [ev("ticket_saved") for _ in range(n)]
    rep = GrowthEngine.build(events)
    assert rep.tickets_saved == n
    assert rep.total_events == n


def test_mixed_counts(ticket_storage):
    events = [ev("ticket_saved"), ev("ticket_saved"),
              ev("claim_confirmed"), ev("report_generated"),
              ev("app_opened")]
    rep = GrowthEngine.build(events)
    assert rep.tickets_saved == 2
    assert rep.claims_completed == 1
    assert rep.reports_viewed == 1


# ---------- 活跃周数 ----------
def test_active_weeks_one(ticket_storage):
    events = [ev("app_opened"), ev("app_opened")]
    assert GrowthEngine.active_weeks(events) == 1


def test_active_weeks_many(ticket_storage):
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=7)]
    assert GrowthEngine.active_weeks(events) == 2


def test_active_weeks_same_week(ticket_storage):
    events = [ev("app_opened", day_offset=0), ev("app_opened", day_offset=1)]
    assert GrowthEngine.active_weeks(events) == 1


@pytest.mark.parametrize("n_weeks", [1, 2, 4, 8])
def test_active_weeks_matrix(ticket_storage, n_weeks):
    events = [ev("app_opened", day_offset=i * 7) for i in range(n_weeks)]
    assert GrowthEngine.active_weeks(events) == n_weeks


# ---------- 连续周数 ----------
def test_streak_zero(ticket_storage):
    assert GrowthEngine.streak_weeks([]) == 0


def test_streak_one(ticket_storage):
    events = [ev("app_opened")]
    assert GrowthEngine.streak_weeks(events) == 1


def test_streak_consecutive(ticket_storage):
    events = [ev("app_opened", day_offset=-14), ev("app_opened", day_offset=-7),
              ev("app_opened")]
    assert GrowthEngine.streak_weeks(events) == 3


def test_streak_broken(ticket_storage):
    events = [ev("app_opened", day_offset=-21), ev("app_opened")]
    assert GrowthEngine.streak_weeks(events) == 1  # 中断，只算最近 1 周


def test_streak_partial(ticket_storage):
    events = [ev("app_opened", day_offset=-7), ev("app_opened")]
    assert GrowthEngine.streak_weeks(events) == 2


@pytest.mark.parametrize("days", [-1, 0, 1])
def test_streak_recent(ticket_storage, days):
    events = [ev("app_opened", day_offset=days)]
    assert GrowthEngine.streak_weeks(events) == 1


def test_streak_only_app_opened(ticket_storage):
    events = [ev("ticket_saved", day_offset=-7), ev("app_opened")]
    assert GrowthEngine.streak_weeks(events) == 1  # 只看 app_opened


# ---------- 成长等级 ----------
def test_level_novice(ticket_storage):
    assert GrowthEngine.level_of(0, 0) == "见习"
    assert GrowthEngine.level_of(1, 0) == "见习"


def test_level_advanced(ticket_storage):
    assert GrowthEngine.level_of(3, 5) == "进阶"


def test_level_active(ticket_storage):
    assert GrowthEngine.level_of(8, 10) == "活跃"


def test_level_senior(ticket_storage):
    assert GrowthEngine.level_of(16, 20) == "资深"


def test_level_longterm(ticket_storage):
    assert GrowthEngine.level_of(26, 30) == "长期用户"


@pytest.mark.parametrize("streak,tickets,expect", [
    (0, 0, "见习"), (1, 1, "见习"), (3, 5, "进阶"), (8, 10, "活跃"),
    (16, 20, "资深"), (26, 30, "长期用户"),
    (2, 20, "资深"),  # 票据数达到资深阈值
    (30, 0, "长期用户"),  # 连续周达到长期用户
])
def test_level_matrix(ticket_storage, streak, tickets, expect):
    assert GrowthEngine.level_of(streak, tickets) == expect


def test_level_from_build(ticket_storage):
    events = [ev("app_opened", day_offset=-7 * i) for i in range(8)] + \
             [ev("ticket_saved") for _ in range(10)]
    rep = GrowthEngine.build(events)
    assert rep.streak_weeks >= 8
    assert rep.level == "活跃"


# ---------- summary_text / to_dict ----------
def test_summary_text_fields(ticket_storage):
    rep = GrowthEngine.build([ev("ticket_saved"), ev("app_opened")])
    text = rep.summary_text()
    assert "保存票据" in text
    assert "连续使用" in text
    assert "成长等级" in text
    assert "随机性" in text


def test_to_dict_fields(ticket_storage):
    rep = GrowthEngine.build([ev("ticket_saved"), ev("app_opened")])
    d = rep.to_dict()
    assert d["tickets_saved"] == 1
    assert d["level"]
    assert "annual" in d


# ---------- 年度 Atlas Report ----------
def test_annual_report_year(ticket_storage):
    events = [ev("ticket_saved")]
    a = GrowthEngine.annual_report(events, date.today().year)
    assert a.year == date.today().year
    assert a.tickets_saved == 1


def test_annual_report_other_year(ticket_storage):
    events = [ev("ticket_saved")]
    a = GrowthEngine.annual_report(events, 1999)
    assert a.tickets_saved == 0


def test_annual_top_activity(ticket_storage):
    events = [ev("ticket_saved"), ev("ticket_saved"), ev("ticket_saved"),
              ev("claim_confirmed"), ev("app_opened")]
    a = GrowthEngine.annual_report(events, date.today().year)
    assert a.top_activity == "保存票据"


def test_annual_in_build(ticket_storage):
    events = [ev("ticket_saved", day_offset=-400)]
    rep = GrowthEngine.build(events)
    assert len(rep.annual) >= 1


def test_annual_to_dict(ticket_storage):
    a = AnnualGrowth(year=2026, tickets_saved=3, claims_completed=1, active_weeks=2)
    d = a.to_dict()
    assert d["year"] == 2026
    assert d["tickets_saved"] == 3
    assert d["top_activity"] == ""


# ---------- EventTracker 集成 ----------
def test_build_from_tracker(ticket_storage):
    EventTracker().clear()
    EventTracker().record("ticket_saved")
    EventTracker().record("ticket_saved")
    EventTracker().record("claim_confirmed")
    rep = GrowthEngine.build()
    assert rep.tickets_saved == 2
    assert rep.claims_completed == 1


def test_helper_function(ticket_storage):
    rep = build_growth([ev("ticket_saved"), ev("app_opened")])
    assert isinstance(rep, GrowthReport)


def test_disclaimer(ticket_storage):
    assert "随机性" in DISCLAIMER


# ---------- 大规模矩阵 ----------
@pytest.mark.parametrize("n", range(20))
def test_build_many_events(ticket_storage, n):
    events = [ev("ticket_saved", day_offset=-(i % 30)) for i in range(n)]
    rep = GrowthEngine.build(events)
    assert rep.tickets_saved == n


@pytest.mark.parametrize("seed", range(15))
def test_random_events(ticket_storage, seed):
    import random
    random.seed(seed)
    events = []
    for i in range(random.randint(1, 30)):
        t = random.choice(["ticket_saved", "app_opened", "claim_confirmed",
                           "report_generated", "reminder_shown"])
        events.append(ev(t, day_offset=-random.randint(0, 60)))
    rep = GrowthEngine.build(events)
    assert rep.total_events == len(events)
    assert rep.streak_weeks >= 0
    assert rep.level in ("见习", "进阶", "活跃", "资深", "长期用户")
    assert rep.summary_text()


@pytest.mark.parametrize("weeks", [1, 2, 3, 4, 6, 8, 10])
def test_streak_by_weekly_open(ticket_storage, weeks):
    events = [ev("app_opened", day_offset=-7 * (weeks - 1 - i))
              for i in range(weeks)]
    assert GrowthEngine.streak_weeks(events) == weeks


# ---------- 补充（≥100） ----------
@pytest.mark.parametrize("offset", [0, -1, -3])
def test_streak_same_week_gap(ticket_storage, offset):
    """同一天多次打开仍算 1 周。"""
    events = [ev("app_opened", day_offset=offset, hour=9),
              ev("app_opened", day_offset=offset, hour=18)]
    assert GrowthEngine.streak_weeks(events) == 1


def test_annual_top_activity_reports(ticket_storage):
    events = [ev("report_generated") for _ in range(4)] + [ev("ticket_saved")]
    a = GrowthEngine.annual_report(events, date.today().year)
    assert a.top_activity == "查看报告"


def test_annual_top_activity_claims(ticket_storage):
    events = [ev("claim_confirmed") for _ in range(3)]
    a = GrowthEngine.annual_report(events, date.today().year)
    assert a.top_activity == "完成兑奖"


def test_unknown_event_type_ignored(ticket_storage):
    events = [UserEvent(event_type="unknown")]
    rep = GrowthEngine.build(events)
    assert rep.total_events == 1
    assert rep.tickets_saved == 0


def test_level_threshold_boundary(ticket_storage):
    """等级阈值边界。"""
    assert GrowthEngine.level_of(2, 4) == "见习"
    assert GrowthEngine.level_of(3, 4) == "进阶"
    assert GrowthEngine.level_of(2, 5) == "进阶"
    assert GrowthEngine.level_of(7, 9) == "进阶"
    assert GrowthEngine.level_of(8, 9) == "活跃"


def test_build_after_clear(ticket_storage):
    EventTracker().clear()
    EventTracker().record("ticket_saved")
    EventTracker().record("ticket_saved")
    EventTracker().record("ticket_saved")
    rep = GrowthEngine.build()
    assert rep.tickets_saved == 3
    assert rep.level == "见习"

