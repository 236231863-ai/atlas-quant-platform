"""v4.8 P3：新用户引导系统测试。

覆盖：三步流程 / onboarding 事件 / 价值导向。
"""
from __future__ import annotations

import pytest

from engine.onboarding.flow_v48 import (
    STEPS, OnboardingFlow, start_onboarding,
)
from engine.user_analytics import AnalyticsTracker


# ---------- 三步流程 ----------
def test_steps_count():
    assert len(STEPS) == 3


def test_step_names():
    names = [s[0] for s in STEPS]
    assert names == ["build_profile", "view_behavior", "enable_reminder"]


def test_first_step():
    flow = OnboardingFlow()
    assert flow.step["name"] == "build_profile"
    assert "建立我的彩票档案" in flow.step["title"]


def test_next():
    flow = OnboardingFlow()
    flow.next()
    assert flow.step["name"] == "view_behavior"


def test_next_through_all():
    flow = OnboardingFlow()
    flow.next()
    flow.next()
    assert flow.step["name"] == "enable_reminder"


def test_next_at_end():
    flow = OnboardingFlow()
    flow.next()
    flow.next()
    flow.next()  # 超出不动
    assert flow.step["name"] == "enable_reminder"


def test_finish():
    flow = OnboardingFlow()
    assert flow.finish() is True
    assert flow.completed is True


# ---------- onboarding 事件 ----------
def test_start_records(ticket_storage):
    AnalyticsTracker().clear()
    start_onboarding()
    assert AnalyticsTracker().count("onboarding_start") == 1


def test_complete_records(ticket_storage):
    AnalyticsTracker().clear()
    flow = start_onboarding()
    flow.finish()
    assert AnalyticsTracker().count("onboarding_complete") == 1


def test_drop_records(ticket_storage):
    AnalyticsTracker().clear()
    flow = start_onboarding()
    flow.drop()
    assert AnalyticsTracker().count("onboarding_drop") == 1


def test_event_types_in_analytics():
    from engine.user_analytics import EVENT_NAMES
    for e in ("onboarding_start", "onboarding_complete", "onboarding_drop"):
        assert e in EVENT_NAMES


# ---------- 价值导向 ----------
def test_no_research_data():
    """引导步骤不含研究数据（和值/奇偶/冷热）。"""
    for _, title, desc in STEPS:
        assert "和值" not in title
        assert "奇偶" not in title
        assert "冷热" not in title


def test_steps_value_oriented():
    for _, title, _ in STEPS:
        assert title  # 有价值标题


# ---------- 矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_flow_stable(ticket_storage, i):
    AnalyticsTracker().clear()
    flow = start_onboarding()
    for _ in range(3):
        flow.next()
    flow.finish()
    assert flow.completed
    assert AnalyticsTracker().count("onboarding_start") == 1


@pytest.mark.parametrize("i", range(10))
def test_drop_flow(ticket_storage, i):
    AnalyticsTracker().clear()
    flow = start_onboarding()
    flow.drop()
    assert not flow.completed
