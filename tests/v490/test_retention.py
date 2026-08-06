"""v4.9 P1 用户留存曲线测试。"""
import pytest

from engine.user_experiment import (
    ExperimentEvent,
    ExperimentRetention,
    ExperimentRetentionBuilder,
    build_retention,
)


def _open(uid, day):
    return ExperimentEvent(event_name="app_open", user_id=uid,
                           timestamp=f"2026-08-{day:02d}T10:00:00")


def _install(uid, day):
    return ExperimentEvent(event_name="app_install", user_id=uid,
                           timestamp=f"2026-08-{day:02d}T10:00:00")


# ---- 基础 ----
def test_no_events():
    r = ExperimentRetentionBuilder.build([])
    assert r.d1 == 0.0 and r.d3 == 0.0 and r.d7 == 0.0


def test_single_day_active():
    events = [_open("u1", 3)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d1 == 0.0
    assert r.cohort_users == 1


def test_d1_full_return():
    events = [_open("u1", 3), _open("u1", 4)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d1 == 1.0


def test_d1_half_return():
    events = [_open("u1", 3), _open("u2", 3), _open("u1", 4)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d1 == pytest.approx(0.5)


def test_d7_return():
    events = [_open("u1", 3), _open("u1", 10)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d7 == 1.0


@pytest.mark.parametrize("days", [1, 3, 5, 7])
def test_d1_all_return_days(days):
    events = [_open("u1", 3), _open("u1", 3 + days)]
    r = ExperimentRetentionBuilder.build(events)
    # D1 只看 day+1
    assert (r.d1 == 1.0) == (days == 1)


# ---- 曲线 ----
def test_curve_includes_day0():
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    assert r.curve[0].day_offset == 0
    assert r.curve[0].rate == 1.0


def test_curve_length():
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    assert len(r.curve) == 8  # 0..7


@pytest.mark.parametrize("offset", [1, 2, 3, 4, 5, 6, 7])
def test_curve_has_all_offsets(offset):
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    offsets = [p.day_offset for p in r.curve]
    assert offset in offsets


def test_curve_day3_matches_d3():
    events = [_open("u1", 3), _open("u1", 6)]
    r = ExperimentRetentionBuilder.build(events)
    p = [p for p in r.curve if p.day_offset == 3][0]
    assert p.rate == pytest.approx(r.d3)


# ---- 多用户 cohort ----
def test_cohort_users():
    events = [_open("u1", 3), _open("u2", 3), _open("u3", 5)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.cohort_users == 3


def test_d1_ratio_mixed():
    # u1,u2 首见 D0(3)；u1 回 D1(4)
    events = [_open("u1", 3), _open("u2", 3), _open("u1", 4)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d1 == pytest.approx(0.5)


def test_different_cohort_days():
    # u1 首见3号，u2 首见5号；u1 回4号(1/2的d1)
    events = [_open("u1", 3), _open("u2", 5), _open("u1", 4)]
    r = ExperimentRetentionBuilder.build(events)
    assert r.d1 == pytest.approx(0.5)


# ---- weekly_return 计入 ----
def test_weekly_return_counts_as_active():
    events = [_install("u1", 3),
              ExperimentEvent(event_name="weekly_return", user_id="u1",
                              timestamp="2026-08-04T10:00:00")]
    r = ExperimentRetentionBuilder.build(events)
    # 无 app_open，默认 weekly_return 不计入 → d1=0
    assert r.d1 == 0.0


def test_weekly_return_included_when_flag():
    events = [_open("u1", 3),
              ExperimentEvent(event_name="weekly_return", user_id="u1",
                              timestamp="2026-08-04T10:00:00")]
    r = ExperimentRetentionBuilder.build(events, use_weekly_return=True)
    assert r.d1 == 1.0


# ---- 过滤 ----
def test_filter_experiment():
    events = [
        ExperimentEvent(event_name="app_open", user_id="u1", experiment_id="exp-A",
                        timestamp="2026-08-03T10:00:00"),
        ExperimentEvent(event_name="app_open", user_id="u1", experiment_id="exp-A",
                        timestamp="2026-08-04T10:00:00"),
        ExperimentEvent(event_name="app_open", user_id="u2", experiment_id="exp-B",
                        timestamp="2026-08-03T10:00:00"),
    ]
    r = ExperimentRetentionBuilder.build(events, experiment_id="exp-A")
    assert r.cohort_users == 1
    assert r.d1 == 1.0


# ---- 序列化 ----
def test_to_dict():
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    d = r.to_dict()
    assert "d1" in d and "d7" in d and "curve" in d


def test_to_text():
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    assert "留存" in r.to_text()


def test_build_helper():
    r = build_retention([_open("u1", 3), _open("u1", 4)])
    assert r.d1 == 1.0


def test_return_type():
    r = ExperimentRetentionBuilder.build([_open("u1", 3)])
    assert isinstance(r, ExperimentRetention)
