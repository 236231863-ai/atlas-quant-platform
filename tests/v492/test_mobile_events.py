"""埋点扩展测试：SOURCE_MOBILE + 5 个 mobile 事件 + normalize_source。"""
from __future__ import annotations

import pytest

from engine.user_experiment.events import (
    EXPERIMENT_EVENTS,
    SOURCE_MOBILE,
    SOURCE_REAL,
    SOURCE_SIMULATION,
    ExperimentEvent,
    ExperimentTracker,
    is_real_source,
    normalize_source,
)

MOBILE_EVENTS = (
    "mobile_opened",
    "mobile_ticket_saved",
    "mobile_reminder_enabled",
    "mobile_draw_viewed",
    "mobile_feedback_submitted",
)


class TestMobileEventsInSet:
    @pytest.mark.parametrize("evt", MOBILE_EVENTS)
    def test_mobile_event_in_experiment_events(self, evt):
        assert evt in EXPERIMENT_EVENTS

    def test_all_five_present(self):
        for evt in MOBILE_EVENTS:
            assert evt in EXPERIMENT_EVENTS
        assert len(EXPERIMENT_EVENTS) == 22  # 17 旧 + 5 新

    def test_old_events_untouched(self):
        assert "app_install" in EXPERIMENT_EVENTS
        assert "weekly_return" in EXPERIMENT_EVENTS
        assert "premium_click" in EXPERIMENT_EVENTS


class TestNormalizeSource:
    def test_mobile_kept(self):
        assert normalize_source("MOBILE") == SOURCE_MOBILE

    def test_mobile_case_sensitive(self):
        assert normalize_source("mobile") == SOURCE_REAL

    def test_desktop_to_real(self):
        assert normalize_source("desktop") == SOURCE_REAL

    def test_empty_to_real(self):
        assert normalize_source("") == SOURCE_REAL

    def test_none_to_real(self):
        assert normalize_source(None) == SOURCE_REAL

    def test_simulation_kept(self):
        assert normalize_source("SIMULATION") == SOURCE_SIMULATION

    def test_unknown_to_real(self):
        assert normalize_source("whatever") == SOURCE_REAL


class TestIsRealSource:
    def test_real_true(self):
        assert is_real_source(SOURCE_REAL) is True

    def test_mobile_true(self):
        assert is_real_source(SOURCE_MOBILE) is True

    def test_simulation_false(self):
        assert is_real_source(SOURCE_SIMULATION) is False

    def test_legacy_desktop_false(self):
        assert is_real_source("desktop") is False  # 未 normalize 前不算


class TestTrackerRealEvents:
    def _tracker_with_events(self, tmp_path):
        t = ExperimentTracker(storage_dir=str(tmp_path))
        t.record("app_open", user_id="u1", source="REAL")
        t.record("app_open", user_id="u2", source="MOBILE")
        t.record("app_open", user_id="u3", source="SIMULATION")
        t.record("app_open", user_id="u4", source="desktop")
        return t

    def test_real_events_includes_mobile(self, tmp_path):
        t = self._tracker_with_events(tmp_path)
        real = t.real_events()
        assert {e.user_id for e in real} == {"u1", "u2", "u4"}

    def test_mobile_events_only(self, tmp_path):
        t = self._tracker_with_events(tmp_path)
        mobile = t.mobile_events()
        assert {e.user_id for e in mobile} == {"u2"}

    def test_simulation_events_only(self, tmp_path):
        t = self._tracker_with_events(tmp_path)
        sim = t.simulation_events()
        assert {e.user_id for e in sim} == {"u3"}

    def test_mobile_event_recorded(self, tmp_path):
        t = ExperimentTracker(storage_dir=str(tmp_path))
        t.record("mobile_opened", user_id="u1", source="MOBILE")
        assert t.count("mobile_opened") == 1

    def test_mobile_shortcut_methods(self, tmp_path):
        # mobile 事件可通过通用 record 记录（无需专用快捷方法）
        t = ExperimentTracker(storage_dir=str(tmp_path))
        for evt in MOBILE_EVENTS:
            assert t.record(evt, user_id="u1", source="MOBILE") is not None
        assert t.count("mobile_feedback_submitted") == 1
