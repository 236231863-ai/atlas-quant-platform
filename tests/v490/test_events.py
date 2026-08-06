"""v4.9 P1 事件系统测试。"""
import os
import csv
import pytest

from engine.user_experiment import (
    EXPERIMENT_EVENTS,
    MILESTONES,
    ExperimentEvent,
    ExperimentTracker,
)


@pytest.fixture()
def tracker(exp_storage):
    return ExperimentTracker()


# ---- 基础记录 ----
def test_record_valid_event(tracker):
    ev = tracker.record("app_open", "u1", "exp-A")
    assert ev is not None
    assert ev.event_name == "app_open"
    assert ev.user_id == "u1"
    assert ev.experiment_id == "exp-A"


def test_record_invalid_event_returns_none(tracker):
    assert tracker.record("not_an_event", "u1") is None


def test_record_persists_to_jsonl(tracker, exp_storage):
    tracker.record("app_open", "u1")
    path = os.path.join(exp_storage, "experiments_v49.jsonl")
    assert os.path.exists(path)


def test_all_returns_events(tracker):
    tracker.record("app_open", "u1")
    tracker.record("ticket_saved", "u1")
    assert len(tracker.all()) == 2


def test_all_empty(tracker):
    assert tracker.all() == []


def test_count(tracker):
    tracker.record("app_open", "u1")
    tracker.record("app_open", "u2")
    tracker.record("ticket_saved", "u1")
    assert tracker.count("app_open") == 2
    assert tracker.count("ticket_saved") == 1


def test_count_filtered_by_experiment(tracker):
    tracker.record("app_open", "u1", "exp-A")
    tracker.record("app_open", "u2", "exp-B")
    assert tracker.count("app_open", "exp-A") == 1


def test_users_unique(tracker):
    tracker.record("app_open", "u1")
    tracker.record("app_open", "u1")
    tracker.record("app_open", "u2")
    assert tracker.users("app_open") == ["u1", "u2"]


def test_users_filter_event(tracker):
    tracker.record("app_open", "u1")
    tracker.record("ticket_saved", "u2")
    assert tracker.users("app_open") == ["u1"]
    assert tracker.users("ticket_saved") == ["u2"]


def test_metadata_roundtrip(tracker):
    tracker.record("ticket_saved", "u1", metadata={"count": 3})
    evs = tracker.all()
    assert evs[0].metadata == {"count": 3}


def test_clear(tracker):
    tracker.record("app_open", "u1")
    tracker.clear()
    assert tracker.all() == []


def test_experiment_id_default(tracker):
    ev = tracker.record("app_open", "u1")
    assert ev.experiment_id == "default"


def test_timestamp_auto(tracker):
    ev = tracker.record("app_open", "u1")
    assert len(ev.timestamp) >= 19  # ISO 格式


# ---- 快捷方法参数化 ----
@pytest.mark.parametrize("method,event", [
    ("install", "app_install"),
    ("open_app", "app_open"),
    ("save_ticket", "ticket_saved"),
    ("reminder_click", "draw_reminder_clicked"),
    ("check_claim", "claim_checked"),
    ("view_report", "report_viewed"),
    ("premium_view", "premium_view"),
    ("premium_click", "premium_click"),
    ("weekly_return", "weekly_return"),
])
def test_shortcut_methods(tracker, method, event):
    ev = getattr(tracker, method)("u1")
    assert ev is not None
    assert ev.event_name == event
    assert tracker.count(event) == 1


@pytest.mark.parametrize("uid", ["u-1", "u-2", "u-3", "u-4"])
def test_shortcut_multiple_users(tracker, uid):
    tracker.open_app(uid)
    assert tracker.users("app_open") == [uid]


@pytest.mark.parametrize("exp", ["exp-A", "exp-B", "exp-C", "default"])
def test_shortcut_experiment_id(tracker, exp):
    tracker.save_ticket("u1", exp)
    evs = tracker.all()
    assert all(e.experiment_id == exp for e in evs)


# ---- 里程碑 ----
@pytest.mark.parametrize("key,event", MILESTONES.items())
def test_milestone_present(tracker, key, event):
    tracker.record(event, "u1", "exp-A")
    ms = tracker.milestones("u1")
    assert ms[key] is not None
    assert ms[key].startswith("2026")


def test_milestone_absent_is_none(tracker):
    ms = tracker.milestones("u1")
    assert all(v is None for v in ms.values())


def test_milestone_uses_earliest(tracker, exp_storage):
    import json
    path = os.path.join(exp_storage, "experiments_v49.jsonl")
    os.makedirs(exp_storage, exist_ok=True)
    for ts in ("2026-08-04T10:00:00", "2026-08-03T10:00:00", "2026-08-05T10:00:00"):
        ev = ExperimentEvent(event_name="app_open", user_id="u1",
                             timestamp=ts)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
    ms = tracker.milestones("u1")
    assert ms["first_open_at"] == "2026-08-03T10:00:00"


def test_milestone_per_user(tracker):
    tracker.record("ticket_saved", "u1")
    tracker.record("ticket_saved", "u2")
    assert tracker.milestones("u1")["first_ticket_saved_at"] is not None
    assert tracker.milestones("u3")["first_ticket_saved_at"] is None


# ---- CSV 导出 ----
def test_export_csv_creates_file(tracker, exp_storage):
    tracker.record("app_open", "u1", "exp-A")
    path = tracker.export_csv()
    assert os.path.exists(path)


def test_export_csv_header(tracker, exp_storage):
    tracker.record("app_open", "u1")
    path = tracker.export_csv()
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["event_name"] == "app_open"
    assert rows[0]["user_id"] == "u1"


def test_export_csv_all_rows(tracker, exp_storage):
    for i in range(5):
        tracker.open_app(f"u{i}")
    path = tracker.export_csv()
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5


def test_export_csv_filter_experiment(tracker, exp_storage):
    tracker.open_app("u1", "exp-A")
    tracker.open_app("u2", "exp-B")
    path = tracker.export_csv(experiment_id="exp-A")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["user_id"] == "u1"


def test_export_csv_custom_path(tracker, exp_storage):
    target = os.path.join(exp_storage, "custom.csv")
    tracker.open_app("u1")
    assert tracker.export_csv(path=target) == target
    assert os.path.exists(target)


# ---- 事件集完整性 ----
def test_experiment_events_contains_required():
    required = {
        "app_install", "app_open", "ticket_saved", "draw_reminder_clicked",
        "claim_checked", "report_viewed", "premium_view",
    }
    assert required.issubset(set(EXPERIMENT_EVENTS))


def test_milestones_cover_first_events():
    assert set(MILESTONES.values()) <= set(EXPERIMENT_EVENTS)


# ---- 事件 dataclass ----
def test_event_to_dict(tracker):
    ev = ExperimentEvent(event_name="app_open", user_id="u1")
    d = ev.to_dict()
    assert d["event_name"] == "app_open"
    assert d["user_id"] == "u1"
    assert "timestamp" in d
