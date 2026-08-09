"""来源隔离测试：funnel / retention / metrics 中 MOBILE 并入真实统计。"""
from __future__ import annotations

import pytest

from engine.user_experiment.events import (
    SOURCE_MOBILE,
    SOURCE_REAL,
    SOURCE_SIMULATION,
    ExperimentTracker,
)
from engine.user_experiment.funnel import ExperimentFunnel
from engine.user_experiment.retention import ExperimentRetentionBuilder


@pytest.fixture
def tracker(tmp_path):
    t = ExperimentTracker(storage_dir=str(tmp_path))
    # REAL 用户 u1
    t.record("app_install", user_id="u1", source="REAL")
    t.record("app_open", user_id="u1", source="REAL")
    t.record("ticket_saved", user_id="u1", source="REAL")
    # MOBILE 用户 u2
    t.record("app_install", user_id="u2", source="MOBILE")
    t.record("app_open", user_id="u2", source="MOBILE")
    t.record("ticket_saved", user_id="u2", source="MOBILE")
    # SIMULATION 用户 u3
    t.record("app_install", user_id="u3", source="SIMULATION")
    t.record("app_open", user_id="u3", source="SIMULATION")
    return t


class TestFunnelIsolation:
    def _stage_users(self, report, event):
        for s in report.stages:
            if s.event == event:
                return s.users
        return 0

    def test_default_real_includes_mobile(self, tracker):
        report = ExperimentFunnel.build(tracker.all())
        # 安装 2（u1 REAL + u2 MOBILE），保存 2
        assert report.total_installs == 2
        assert self._stage_users(report, "ticket_saved") == 2

    def test_explicit_simulation_only(self, tracker):
        report = ExperimentFunnel.build(tracker.all(), source=SOURCE_SIMULATION)
        assert report.total_installs == 1

    def test_none_all(self, tracker):
        report = ExperimentFunnel.build(tracker.all(), source=None)
        assert report.total_installs == 3


class TestRetentionIsolation:
    def test_real_includes_mobile(self, tracker):
        ret = ExperimentRetentionBuilder.build(tracker.all())
        assert ret.cohort_users == 2

    def test_simulation_separate(self, tracker):
        ret = ExperimentRetentionBuilder.build(tracker.all(), source=SOURCE_SIMULATION)
        assert ret.cohort_users == 1

    def test_mobile_alone(self, tracker):
        ret = ExperimentRetentionBuilder.build(tracker.all(), source=SOURCE_MOBILE)
        assert ret.cohort_users == 1


class TestTrackerSourceMethods:
    def test_real_events_count(self, tracker):
        real = tracker.real_events()
        assert {e.user_id for e in real if e.event_name == "app_install"} == {"u1", "u2"}

    def test_mobile_events_count(self, tracker):
        mobile = tracker.mobile_events()
        assert {e.user_id for e in mobile if e.event_name == "app_install"} == {"u2"}

    def test_simulation_events_count(self, tracker):
        sim = tracker.simulation_events()
        assert {e.user_id for e in sim if e.event_name == "app_install"} == {"u3"}
