"""v3.7.0 Phase 4 测试：UserFeedbackTracker / UserBehaviorReport（≥150）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.user_feedback_v2 import (
    UserFeedbackTracker, UserBehaviorReport, build_behavior_report, EVENT_TYPES,
)


@pytest.fixture
def tracker(tmp_path):
    t = UserFeedbackTracker(storage_dir=str(tmp_path))
    t.clear()
    return t


# ---------- 事件类型 ----------
@pytest.mark.parametrize("t", ["page_view", "feature_use", "report_export", "strategy_view", "preference"])
def test_event_types_valid(t):
    assert t in EVENT_TYPES


@pytest.mark.parametrize("t", ["bad", "", "unknown", "click"])
def test_event_types_invalid(t):
    assert t not in EVENT_TYPES


# ---------- 记录 ----------
@pytest.mark.parametrize("t", ["page_view", "feature_use", "report_export", "strategy_view", "preference"])
def test_record_valid(tracker, t):
    assert tracker.record(t, key="k", value="v") is True


@pytest.mark.parametrize("t", ["bad_type", "", "x"])
def test_record_invalid(tracker, t):
    assert tracker.record(t) is False


@pytest.mark.parametrize("page", ["Dashboard", "Data Analysis", "Strategy Lab", "Backtest Center", "AI Assistant", "Reports"])
def test_page_view(tracker, page):
    assert tracker.page_view(page) is True
    events = tracker.load()
    assert len(events) == 1
    assert events[0]["type"] == "page_view"
    assert events[0]["page"] == page


@pytest.mark.parametrize("feature", ["generate_report", "run_backtest", "import_data", "export", "chat"])
def test_feature_use(tracker, feature):
    assert tracker.feature_use(feature) is True


@pytest.mark.parametrize("fmt", ["md", "pdf", "csv", "png"])
def test_report_export(tracker, fmt):
    assert tracker.report_export(fmt) is True
    events = tracker.load()
    assert events[0]["fmt"] == fmt


@pytest.mark.parametrize("strategy", ["hot", "cold", "balanced"])
def test_strategy_view(tracker, strategy):
    assert tracker.strategy_view(strategy) is True
    assert tracker.load()[0]["strategy"] == strategy


@pytest.mark.parametrize("key,value", [("lottery", "dlt"), ("theme", "dark"), ("lang", "zh-CN")])
def test_preference(tracker, key, value):
    assert tracker.set_preference(key, value) is True
    assert tracker.load()[0]["key"] == key


# ---------- 多条记录 ----------
@pytest.mark.parametrize("n", [1, 5, 20, 100])
def test_record_many(tracker, n):
    for i in range(n):
        tracker.page_view(f"Page{i % 6}")
    assert len(tracker.load()) == n


@pytest.mark.parametrize("limit", [None, 1, 5, 50])
def test_load_limit(tracker, limit):
    for i in range(50):
        tracker.feature_use(f"f{i}")
    events = tracker.load(limit=limit)
    if limit:
        assert len(events) == limit
    else:
        assert len(events) == 50


@pytest.mark.parametrize("n", [3, 10])
def test_record_order(tracker, n):
    for i in range(n):
        tracker.page_view(f"p{i}")
    events = tracker.load()
    assert [e["page"] for e in events] == [f"p{i}" for i in range(n)]


def test_clear(tracker):
    tracker.page_view("Dashboard")
    assert len(tracker.load()) == 1
    tracker.clear()
    assert tracker.load() == []


def test_clear_empty(tracker):
    tracker.clear()
    assert tracker.load() == []


# ---------- 持久化 ----------
@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    t1 = UserFeedbackTracker(storage_dir=str(tmp_path))
    for i in range(n):
        t1.page_view(f"p{i}")
    t2 = UserFeedbackTracker(storage_dir=str(tmp_path))
    assert len(t2.load()) == n


# ---------- 报告构建 ----------
@pytest.mark.parametrize("n", [0, 1, 10, 50])
def test_report_empty(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    r = build_behavior_report(tracker)
    assert r.total_events == n


@pytest.mark.parametrize("pages", [
    ["Dashboard"] * 5,
    ["Dashboard", "Data Analysis", "Strategy Lab"],
    ["Reports", "Reports", "Dashboard"],
])
def test_top_pages(tracker, pages):
    for p in pages:
        tracker.page_view(p)
    r = build_behavior_report(tracker)
    # 校验最高计数正确（并列时不要求具体哪个元素）
    assert r.top_pages[0][1] == max(pages.count(x) for x in set(pages))
    # 且该元素确实在 pages 中
    assert r.top_pages[0][0] in set(pages)


@pytest.mark.parametrize("features", [
    ["export"] * 3 + ["backtest"] * 1,
    ["report"] * 2,
])
def test_top_features(tracker, features):
    for f in features:
        tracker.feature_use(f)
    r = build_behavior_report(tracker)
    assert r.top_features[0][0] == max(set(features), key=features.count)


@pytest.mark.parametrize("fmts", [["md", "md", "pdf"], ["csv"], ["png", "png", "png", "md"]])
def test_export_formats(tracker, fmts):
    for f in fmts:
        tracker.report_export(f)
    r = build_behavior_report(tracker)
    assert r.export_formats.get("md", 0) == fmts.count("md")


@pytest.mark.parametrize("strategies", [["hot", "hot", "cold"], ["balanced"]])
def test_top_strategies(tracker, strategies):
    for s in strategies:
        tracker.strategy_view(s)
    r = build_behavior_report(tracker)
    assert r.top_strategies[0][0] == max(set(strategies), key=strategies.count)


@pytest.mark.parametrize("prefs", [
    [("lottery", "dlt"), ("theme", "dark")],
    [("lang", "zh")],
])
def test_preferences(tracker, prefs):
    for k, v in prefs:
        tracker.set_preference(k, v)
    r = build_behavior_report(tracker)
    for k, v in prefs:
        assert r.preferences[k] == v


# ---------- 活跃天数 ----------
@pytest.mark.parametrize("days", [["2026-08-01"], ["2026-08-01", "2026-08-02"], ["2026-08-01"] * 5])
def test_active_days(tracker, days):
    for d in days:
        tracker.record("page_view", page="Dashboard", ts=f"{d} 10:00:00")
    r = build_behavior_report(tracker)
    assert r.active_days == len(set(days))


# ---------- 输出格式 ----------
@pytest.mark.parametrize("n", [0, 5, 50])
def test_report_text(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    text = build_behavior_report(tracker).to_text()
    assert "Atlas" in text
    assert "本机" in text


@pytest.mark.parametrize("key", ["total_events", "by_type", "top_pages", "active_days"])
def test_report_dict(tracker, key):
    tracker.page_view("Dashboard")
    d = build_behavior_report(tracker).to_dict()
    assert key in d


# ---------- 报告直接构造 ----------
@pytest.mark.parametrize("events", [
    [{"type": "page_view", "page": "A", "ts": "2026-01-01 00:00:00"}],
    [{"type": "feature_use", "feature": "f", "ts": "2026-01-01 00:00:00"}],
    [],
])
def test_report_from_events(events):
    r = build_behavior_report(events=events)
    assert r.total_events == len(events)


@pytest.mark.parametrize("n", [1, 10, 100])
def test_report_by_type(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    r = build_behavior_report(tracker)
    assert r.by_type.get("page_view") == n


# ---------- 扩展：事件组合 ----------
@pytest.mark.parametrize("n_pv,n_fu,n_re,n_sv,n_pr", [
    (3, 2, 1, 1, 0), (0, 5, 0, 0, 1), (10, 0, 5, 2, 1), (1, 1, 1, 1, 1),
])
def test_mixed_events(tracker, n_pv, n_fu, n_re, n_sv, n_pr):
    for i in range(n_pv): tracker.page_view(f"p{i%6}")
    for i in range(n_fu): tracker.feature_use(f"f{i%4}")
    for i in range(n_re): tracker.report_export(["md","pdf","csv"][i%3])
    for i in range(n_sv): tracker.strategy_view(["hot","cold","balanced"][i%3])
    for i in range(n_pr): tracker.set_preference(f"k{i}", i)
    r = build_behavior_report(tracker)
    assert r.total_events == n_pv + n_fu + n_re + n_sv + n_pr
    assert r.by_type.get("page_view", 0) == n_pv
    assert r.by_type.get("feature_use", 0) == n_fu
    assert r.by_type.get("report_export", 0) == n_re
    assert r.by_type.get("strategy_view", 0) == n_sv
    assert r.by_type.get("preference", 0) == n_pr


@pytest.mark.parametrize("n", [0, 5, 15, 30])
def test_report_text_lines(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    text = build_behavior_report(tracker).to_text()
    assert len(text.split("\n")) >= 3


# ---------- 扩展：报告网格 ----------
@pytest.mark.parametrize("pages", [
    ["A", "A", "B"], ["A"] * 3 + ["B"] * 2, ["X"] * 10 + ["Y"] * 5,
])
def test_top_pages_rank(tracker, pages):
    for p in pages:
        tracker.page_view(p)
    r = build_behavior_report(tracker)
    ranked = sorted(set(pages), key=lambda p: -pages.count(p))
    assert r.top_pages[0][0] == ranked[0]
    assert r.top_pages[0][1] == pages.count(ranked[0])


@pytest.mark.parametrize("features", [
    ["a"] * 3 + ["b"] * 3, ["a"] * 5, ["a", "b", "c", "d"],
])
def test_top_features_rank(tracker, features):
    for f in features:
        tracker.feature_use(f)
    r = build_behavior_report(tracker)
    assert r.top_features[0][1] == max(features.count(x) for x in set(features))


@pytest.mark.parametrize("n", [1, 3, 10])
def test_export_formats_all(tracker, n):
    for i in range(n):
        tracker.report_export("pdf")
        tracker.report_export("md")
    r = build_behavior_report(tracker)
    assert r.export_formats["pdf"] == n
    assert r.export_formats["md"] == n


# ---------- 扩展：类型计数 ----------
@pytest.mark.parametrize("event_type", list(EVENT_TYPES))
def test_type_counter(tracker, event_type):
    tracker.record(event_type, k="v")
    r = build_behavior_report(tracker)
    assert r.by_type[event_type] == 1


@pytest.mark.parametrize("n", [2, 7, 12])
def test_multiple_types_counter(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
        tracker.feature_use("f")
    r = build_behavior_report(tracker)
    assert r.by_type["page_view"] == n
    assert r.by_type["feature_use"] == n


# ---------- 扩展：持久化与重建 ----------
@pytest.mark.parametrize("n", [1, 10, 30])
def test_rebuild_report(tmp_path, n):
    t = UserFeedbackTracker(storage_dir=str(tmp_path))
    for i in range(n):
        t.page_view(f"p{i%6}")
    r1 = build_behavior_report(t)
    r2 = build_behavior_report(UserFeedbackTracker(storage_dir=str(tmp_path)))
    assert r1.total_events == r2.total_events == n


@pytest.mark.parametrize("n", [0, 5])
def test_report_after_clear(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    tracker.clear()
    r = build_behavior_report(tracker)
    assert r.total_events == 0


# ---------- 扩展：事件字段 ----------
@pytest.mark.parametrize("extra", [
    {"a": 1}, {"a": "x", "b": 2}, {"k": [1, 2]}, {},
])
def test_record_extra_fields(tracker, extra):
    assert tracker.record("feature_use", feature="f", **extra) is True
    e = tracker.load()[0]
    for k, v in extra.items():
        assert e[k] == v


@pytest.mark.parametrize("n", [3, 8, 15])
def test_ts_present(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    for e in tracker.load():
        assert "ts" in e
        assert len(e["ts"]) >= 10


# ---------- 扩展2：更多组合 ----------
@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_all_page_views(tracker, n):
    pages = ["Dashboard", "Data Analysis", "Strategy Lab", "Backtest Center", "AI Assistant", "Reports"]
    for p in pages[:n]:
        tracker.page_view(p)
    r = build_behavior_report(tracker)
    assert r.total_events == n
    assert len(r.top_pages) == n


@pytest.mark.parametrize("n", [1, 3, 5])
def test_all_features(tracker, n):
    features = ["generate_report", "run_backtest", "import_data", "export", "chat"]
    for f in features[:n]:
        tracker.feature_use(f)
    r = build_behavior_report(tracker)
    assert len(r.top_features) == n


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_all_export_formats(tracker, n):
    fmts = ["md", "pdf", "csv", "png"]
    for f in fmts[:n]:
        tracker.report_export(f)
    r = build_behavior_report(tracker)
    assert len(r.export_formats) == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_strategies(tracker, n):
    for s in ["hot", "cold", "balanced"][:n]:
        tracker.strategy_view(s)
    r = build_behavior_report(tracker)
    assert len(r.top_strategies) == n


@pytest.mark.parametrize("key", ["total_events", "by_type", "top_pages", "top_features", "export_formats", "top_strategies", "preferences", "active_days"])
def test_dict_all_keys(tracker, key):
    tracker.page_view("Dashboard")
    tracker.feature_use("f")
    tracker.report_export("md")
    tracker.strategy_view("hot")
    tracker.set_preference("k", "v")
    d = build_behavior_report(tracker).to_dict()
    assert key in d


@pytest.mark.parametrize("n", [5, 20, 60])
def test_report_text_length(tracker, n):
    for i in range(n):
        tracker.page_view("Dashboard")
    text = build_behavior_report(tracker).to_text()
    assert "总事件" in text
    assert str(n) in text


@pytest.mark.parametrize("i", range(6))
def test_page_counts(tracker, i):
    pages = ["Dashboard", "Data Analysis", "Strategy Lab", "Backtest Center", "AI Assistant", "Reports"]
    tracker.page_view(pages[i])
    r = build_behavior_report(tracker)
    assert r.top_pages[0][0] == pages[i]
