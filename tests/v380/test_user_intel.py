"""v3.8.0 Phase 1 测试：user_intelligence/v3（≥200）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary, EVENTS

@pytest.fixture
def ui(tmp_path):
    u = UserIntelligenceV3(storage_dir=str(tmp_path)); u.clear(); return u

@pytest.mark.parametrize("e", sorted(EVENTS))
def test_events_valid(e): assert e in EVENTS

@pytest.mark.parametrize("e", ["BAD", "", "click", "x"])
def test_events_invalid(e): assert e not in EVENTS

@pytest.mark.parametrize("e", sorted(EVENTS))
def test_track_valid(ui, e): assert ui.track(e) is True

@pytest.mark.parametrize("e", ["BAD", "unknown"])
def test_track_invalid(ui, e): assert ui.track(e) is False

@pytest.mark.parametrize("n", [1, 5, 20])
def test_app_start(ui, n):
    for _ in range(n): ui.app_start()
    assert len(ui.load()) == n

@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_analysis_run(ui, method):
    assert ui.analysis_run(method) is True
    assert ui.load()[0]["method"] == method

@pytest.mark.parametrize("fmt", ["md", "pdf", "csv", "png"])
def test_report_export(ui, fmt):
    assert ui.report_export(fmt) is True
    assert ui.load()[0]["fmt"] == fmt

@pytest.mark.parametrize("method", ["hot", "cold"])
def test_backtest_run(ui, method):
    assert ui.backtest_run(method) is True

@pytest.mark.parametrize("name", ["热号追击", "冷号潜伏"])
def test_strategy_save(ui, name):
    assert ui.strategy_save(name) is True

@pytest.mark.parametrize("ftype", ["bug", "feature", "rating"])
def test_feedback_send(ui, ftype):
    assert ui.feedback_send(ftype) is True

@pytest.mark.parametrize("n", [1, 10, 50])
def test_record_many(ui, n):
    for _ in range(n): ui.app_start()
    assert len(ui.load()) == n

@pytest.mark.parametrize("limit", [None, 1, 5])
def test_load_limit(ui, limit):
    for _ in range(30): ui.app_start()
    ev = ui.load(limit=limit)
    assert len(ev) == (30 if limit is None else limit)

def test_clear(ui):
    ui.app_start(); assert len(ui.load()) == 1
    ui.clear(); assert ui.load() == []

@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    a = UserIntelligenceV3(storage_dir=str(tmp_path))
    for _ in range(n): a.app_start()
    b = UserIntelligenceV3(storage_dir=str(tmp_path))
    assert len(b.load()) == n

@pytest.mark.parametrize("n", [0, 1, 10])
def test_summary(ui, n):
    for _ in range(n): ui.app_start()
    s = build_behavior_summary(ui)
    assert s.total_events == n
    assert s.by_event.get("APP_START", 0) == n

@pytest.mark.parametrize("days", [["2026-08-01"], ["2026-08-01", "2026-08-02"]])
def test_summary_active_days(ui, days):
    for d in days: ui.track("APP_START", ts=f"{d} 10:00:00")
    assert build_behavior_summary(ui).active_days == len(set(days))

@pytest.mark.parametrize("methods", [["hot", "hot", "cold"], ["balanced"]])
def test_top_methods(ui, methods):
    for m in methods: ui.backtest_run(m)
    s = build_behavior_summary(ui)
    assert s.top_methods[0][0] == max(set(methods), key=methods.count)

@pytest.mark.parametrize("fmts", [["md", "md", "pdf"], ["csv"]])
def test_top_formats(ui, fmts):
    for f in fmts: ui.report_export(f)
    s = build_behavior_summary(ui)
    assert s.top_export_formats[0][0] == max(set(fmts), key=fmts.count)

@pytest.mark.parametrize("n", [0, 5])
def test_summary_text(ui, n):
    for _ in range(n): ui.app_start()
    text = build_behavior_summary(ui).to_text()
    assert "Atlas" in text

@pytest.mark.parametrize("events", [[], [{"event": "APP_START", "ts": "2026-01-01 00:00:00"}]])
def test_summary_from_events(events):
    assert build_behavior_summary(events=events).total_events == len(events)

@pytest.mark.parametrize("i", range(5))
def test_full_session(ui, i):
    ui.app_start(); ui.analysis_run("hot"); ui.backtest_run("hot")
    ui.report_export("pdf"); ui.feedback_send("bug")
    assert len(ui.load()) == 5
