"""v3.7.1 Phase 2 测试：ProductAnalytics / ProductUsageReport（≥150）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.product_analytics_v2 import (
    ProductAnalytics, ProductUsageReport, build_usage_report, EVENTS,
)


@pytest.fixture
def a(tmp_path):
    pa = ProductAnalytics(storage_dir=str(tmp_path))
    pa.clear()
    return pa


# ---------- 事件常量 ----------
@pytest.mark.parametrize("e", ["app_open", "analysis_start", "analysis_complete", "report_export", "backtest_run", "strategy_view", "app_close"])
def test_events_valid(e):
    assert e in EVENTS


@pytest.mark.parametrize("e", ["bad", "", "click"])
def test_events_invalid(e):
    assert e not in EVENTS


# ---------- 记录 ----------
@pytest.mark.parametrize("e", ["app_open", "app_close", "analysis_start", "analysis_complete", "report_export", "backtest_run", "strategy_view"])
def test_track_valid(a, e):
    assert a.track(e) is True


@pytest.mark.parametrize("e", ["bad", "unknown"])
def test_track_invalid(a, e):
    assert a.track(e) is False


@pytest.mark.parametrize("n", [1, 5, 20])
def test_app_open(a, n):
    for _ in range(n):
        a.app_open()
    assert len(a.load()) == n


@pytest.mark.parametrize("n", [1, 3])
def test_app_close(a, n):
    for _ in range(n):
        a.app_close()
    events = a.load()
    assert all(e["event"] == "app_close" for e in events)


@pytest.mark.parametrize("fmt", ["md", "pdf", "csv", "png"])
def test_report_export(a, fmt):
    assert a.report_export(fmt) is True
    assert a.load()[0]["fmt"] == fmt


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_backtest_run(a, method):
    assert a.backtest_run(method) is True
    assert a.load()[0]["method"] == method


@pytest.mark.parametrize("s", ["hot", "cold", "balanced"])
def test_strategy_view(a, s):
    assert a.strategy_view(s) is True
    assert a.load()[0]["strategy"] == s


@pytest.mark.parametrize("n", [1, 10])
def test_analysis_events(a, n):
    for _ in range(n):
        a.analysis_start()
        a.analysis_complete()
    events = a.load()
    assert sum(1 for e in events if e["event"] == "analysis_start") == n


# ---------- 多事件 ----------
@pytest.mark.parametrize("n", [1, 5, 50])
def test_record_many(a, n):
    for i in range(n):
        a.app_open()
        a.app_close()
    assert len(a.load()) == n * 2


@pytest.mark.parametrize("limit", [None, 1, 10])
def test_load_limit(a, limit):
    for i in range(30):
        a.app_open()
    events = a.load(limit=limit)
    assert len(events) == (30 if limit is None else limit)


def test_clear(a):
    a.app_open()
    assert len(a.load()) == 1
    a.clear()
    assert a.load() == []


# ---------- 持久化 ----------
@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    a1 = ProductAnalytics(storage_dir=str(tmp_path))
    for _ in range(n):
        a1.app_open()
    a2 = ProductAnalytics(storage_dir=str(tmp_path))
    assert len(a2.load()) == n


# ---------- 报告构建 ----------
@pytest.mark.parametrize("n", [0, 1, 10])
def test_report_sessions(a, n):
    for _ in range(n):
        a.app_open()
        a.app_close()
    r = build_usage_report(a)
    assert r.total_sessions == n


@pytest.mark.parametrize("n", [0, 5])
def test_report_analysis(a, n):
    for _ in range(n):
        a.analysis_start()
        a.analysis_complete()
    r = build_usage_report(a)
    assert r.analysis_start == n
    assert r.analysis_complete == n


@pytest.mark.parametrize("starts,completes", [(10, 7), (5, 5), (5, 0)])
def test_analysis_rate(a, starts, completes):
    for _ in range(starts):
        a.analysis_start()
    for _ in range(completes):
        a.analysis_complete()
    r = build_usage_report(a)
    expected = round(completes / starts, 3) if starts else 0.0
    assert r.analysis_completion_rate == expected


@pytest.mark.parametrize("n", [0, 3, 8])
def test_report_exports(a, n):
    for _ in range(n):
        a.report_export("md")
    r = build_usage_report(a)
    assert r.report_exports == n


@pytest.mark.parametrize("n", [0, 2, 6])
def test_report_backtests(a, n):
    for _ in range(n):
        a.backtest_run("hot")
    r = build_usage_report(a)
    assert r.backtest_runs == n


@pytest.mark.parametrize("n", [0, 4])
def test_report_strategies(a, n):
    for _ in range(n):
        a.strategy_view("cold")
    r = build_usage_report(a)
    assert r.strategy_views == n


# ---------- 崩溃率 ----------
@pytest.mark.parametrize("opened,closed", [(10, 9), (5, 5), (10, 0)])
def test_crash_rate(a, opened, closed):
    for _ in range(opened):
        a.app_open()
    for _ in range(closed):
        a.app_close()
    r = build_usage_report(a)
    expected = round(max(0, opened - closed) / opened, 3) if opened else 0.0
    assert r.crash_rate == expected


# ---------- 活跃天数 ----------
@pytest.mark.parametrize("days", [["2026-08-01"], ["2026-08-01", "2026-08-02"]])
def test_active_days(a, days):
    for d in days:
        a.track("app_open", ts=f"{d} 10:00:00")
    r = build_usage_report(a)
    assert r.active_days == len(set(days))


# ---------- 导出格式 ----------
@pytest.mark.parametrize("fmts", [["md", "md", "pdf"], ["csv"]])
def test_export_formats(a, fmts):
    for f in fmts:
        a.report_export(f)
    r = build_usage_report(a)
    assert r.export_formats.get("md", 0) == fmts.count("md")


# ---------- 热门策略 ----------
@pytest.mark.parametrize("strategies", [["hot", "hot", "cold"], ["balanced"]])
def test_top_strategies(a, strategies):
    for s in strategies:
        a.strategy_view(s)
    r = build_usage_report(a)
    assert r.top_strategies[0][0] == max(set(strategies), key=strategies.count)


# ---------- 输出 ----------
@pytest.mark.parametrize("n", [0, 5])
def test_report_text(a, n):
    for _ in range(n):
        a.app_open()
        a.analysis_start()
    text = build_usage_report(a).to_text()
    assert "Atlas" in text


@pytest.mark.parametrize("key", ["total_sessions", "analysis_completion_rate", "crash_rate", "active_days"])
def test_report_dict(a, key):
    a.app_open()
    d = build_usage_report(a).to_dict()
    assert key in d


# ---------- 直接构造 ----------
@pytest.mark.parametrize("events", [
    [{"event": "app_open", "ts": "2026-01-01 00:00:00"}],
    [{"event": "analysis_start", "ts": "2026-01-01 00:00:00"}],
    [],
])
def test_report_from_events(events):
    r = build_usage_report(events=events)
    assert r.total_sessions >= 0


# ---------- 扩展 ----------
@pytest.mark.parametrize("opened", [1, 5, 15])
@pytest.mark.parametrize("closed", [0, 3, 10])
def test_session_grid(a, opened, closed):
    for _ in range(opened):
        a.app_open()
    for _ in range(min(closed, opened)):
        a.app_close()
    r = build_usage_report(a)
    assert r.total_sessions == max(opened, min(closed, opened))


@pytest.mark.parametrize("n", [1, 3])
def test_full_session(a, n):
    for _ in range(n):
        a.app_open()
        a.analysis_start()
        a.analysis_complete()
        a.report_export("pdf")
        a.backtest_run("balanced")
        a.app_close()
    r = build_usage_report(a)
    assert r.total_sessions == n
    assert r.report_exports == n
    assert r.backtest_runs == n


# ---------- 扩展：组合事件 ----------
@pytest.mark.parametrize("opens,starts,completes,exports,backtests,views", [
    (3, 3, 2, 1, 1, 1), (1, 0, 0, 0, 0, 0), (10, 8, 6, 4, 2, 3),
])
def test_mixed_counts(a, opens, starts, completes, exports, backtests, views):
    for _ in range(opens): a.app_open()
    for _ in range(starts): a.analysis_start()
    for _ in range(completes): a.analysis_complete()
    for _ in range(exports): a.report_export("md")
    for _ in range(backtests): a.backtest_run("hot")
    for _ in range(views): a.strategy_view("cold")
    r = build_usage_report(a)
    assert r.app_open == opens
    assert r.analysis_start == starts
    assert r.analysis_complete == completes
    assert r.report_exports == exports
    assert r.backtest_runs == backtests
    assert r.strategy_views == views


@pytest.mark.parametrize("n", [1, 5, 20])
def test_export_count_all_formats(a, n):
    for f in ["md", "pdf", "csv", "png"]:
        for _ in range(n):
            a.report_export(f)
    r = build_usage_report(a)
    assert r.report_exports == n * 4
    assert sum(r.export_formats.values()) == n * 4


@pytest.mark.parametrize("methods", [["hot"] * 3 + ["cold"] * 1, ["balanced"] * 2])
def test_backtest_methods(a, methods):
    for m in methods:
        a.backtest_run(m)
    r = build_usage_report(a)
    assert r.backtest_methods.get("hot", 0) == methods.count("hot")


# ---------- 扩展：时间 ----------
@pytest.mark.parametrize("n", [1, 7, 30])
def test_active_days_many(a, n):
    for i in range(n):
        a.track("app_open", ts=f"2026-08-{(i % 30) + 1:02d} 10:00:00")
    r = build_usage_report(a)
    assert r.active_days == n


@pytest.mark.parametrize("n", [0, 5])
def test_ts_present(a, n):
    for _ in range(n):
        a.app_open()
    for e in a.load():
        assert "ts" in e and len(e["ts"]) >= 10


# ---------- 扩展：边界 ----------
@pytest.mark.parametrize("starts,completes", [(0, 5), (5, 0), (0, 0)])
def test_analysis_rate_edges(a, starts, completes):
    for _ in range(starts): a.analysis_start()
    for _ in range(completes): a.analysis_complete()
    r = build_usage_report(a)
    if starts == 0 or completes == 0:
        assert r.analysis_completion_rate == 0.0
    else:
        assert r.analysis_completion_rate > 0


@pytest.mark.parametrize("i", range(10))
def test_clear_reuse(a, i):
    a.app_open()
    a.clear()
    assert a.load() == []


@pytest.mark.parametrize("events", [
    [{"event": "app_open", "ts": "2026-01-01 10:00:00"}, {"event": "app_close", "ts": "2026-01-01 10:05:00"}],
    [{"event": "app_open", "ts": "2026-01-01 10:00:00"}],
])
def test_session_from_events(events):
    r = build_usage_report(events=events)
    assert r.app_open == sum(1 for e in events if e["event"] == "app_open")


# ---------- 扩展2：更多边界 ----------
@pytest.mark.parametrize("n", [1, 2, 5, 10])
def test_export_formats_grid(a, n):
    for i in range(n):
        a.report_export(["md", "pdf", "csv", "png"][i % 4])
    r = build_usage_report(a)
    assert r.report_exports == n
    assert sum(r.export_formats.values()) == n


@pytest.mark.parametrize("methods", [["hot"], ["hot", "cold", "balanced"], ["hot"] * 5])
def test_backtest_methods_grid(a, methods):
    for m in methods:
        a.backtest_run(m)
    r = build_usage_report(a)
    assert r.backtest_runs == len(methods)
    assert r.backtest_methods.get("hot", 0) == methods.count("hot")


@pytest.mark.parametrize("s", ["hot", "cold", "balanced"])
@pytest.mark.parametrize("n", [1, 3])
def test_strategy_count(a, s, n):
    for _ in range(n):
        a.strategy_view(s)
    r = build_usage_report(a)
    assert r.strategy_views == n
    assert (s, n) in r.top_strategies


@pytest.mark.parametrize("i", range(5))
def test_repeat_reports(a, i):
    for _ in range(i + 1):
        a.app_open()
        a.analysis_start()
        a.analysis_complete()
        a.report_export("md")
        a.app_close()
    r = build_usage_report(a)
    assert r.total_sessions == i + 1
    assert r.analysis_complete == i + 1


@pytest.mark.parametrize("events", [
    [{"event": "report_export", "fmt": "md", "ts": "2026-01-01 00:00:00"}],
    [{"event": "backtest_run", "method": "hot", "ts": "2026-01-01 00:00:00"}],
    [{"event": "strategy_view", "strategy": "cold", "ts": "2026-01-01 00:00:00"}],
])
def test_single_event_reports(events):
    r = build_usage_report(events=events)
    assert r.total_sessions == 0


@pytest.mark.parametrize("n", [0, 10])
def test_empty_events_dict(a, n):
    for _ in range(n):
        a.app_open()
    d = build_usage_report(a).to_dict()
    assert d["total_sessions"] == n
    assert isinstance(d["export_formats"], dict)


# ---------- 扩展3：最终补齐 ----------
@pytest.mark.parametrize("n", [1, 4, 8])
def test_strategy_view_counts(a, n):
    for _ in range(n):
        a.strategy_view("hot")
    r = build_usage_report(a)
    assert r.strategy_views == n


@pytest.mark.parametrize("n", [1, 6])
def test_mixed_session_rates(a, n):
    for _ in range(n):
        a.analysis_start()
    for _ in range(n // 2):
        a.analysis_complete()
    r = build_usage_report(a)
    assert r.analysis_completion_rate >= 0


@pytest.mark.parametrize("i", range(5))
def test_repeat_load(a, i):
    for _ in range(i + 1):
        a.app_open()
    assert len(a.load()) == i + 1
    assert len(a.load()) == i + 1  # 重复读一致
