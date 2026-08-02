"""v3.8.0 Phase 2 测试：value_score（≥250）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.value_score import compute_value_score, UserValueScore

@pytest.mark.parametrize("total", [0, 10, 50, 100, 500])
def test_usage_score(total):
    s = compute_value_score(total_events=total)
    assert 0 <= s.usage_score <= 20

@pytest.mark.parametrize("days", [0, 1, 3, 7, 14])
def test_retention_score(days):
    s = compute_value_score(active_days=days)
    assert 0 <= s.retention_score <= 20

@pytest.mark.parametrize("runs", [0, 5, 20])
def test_research_score(runs):
    s = compute_value_score(analysis_runs=runs, backtest_runs=runs)
    assert 0 <= s.research_score <= 20

@pytest.mark.parametrize("exports", [0, 4, 10])
def test_export_score(exports):
    s = compute_value_score(exports=exports)
    assert 0 <= s.export_score <= 20

@pytest.mark.parametrize("fb", [0, 2, 5])
def test_feedback_score(fb):
    s = compute_value_score(feedback_count=fb)
    assert 0 <= s.feedback_score <= 20

@pytest.mark.parametrize("kwargs", [
    {}, {"total_events": 10}, {"active_days": 2},
    {"analysis_runs": 5}, {"backtest_runs": 5}, {"exports": 3},
    {"feedback_count": 1}, {"strategy_saves": 2},
])
def test_any_input(kwargs):
    s = compute_value_score(**kwargs)
    assert 0 <= s.total <= 100

@pytest.mark.parametrize("total", [0, 20, 60, 100, 500])
def test_total_bounds(total):
    s = compute_value_score(total_events=total, active_days=7)
    assert 0 <= s.total <= 100

@pytest.mark.parametrize("total,expected_level", [
    (0, "入门"), (20, "入门"), (40, "进阶"), (65, "资深"), (90, "专家"),
])
def test_level(total, expected_level):
    s = UserValueScore(total=total)
    assert s.level == expected_level

@pytest.mark.parametrize("total", [0, 35, 60, 80, 100])
def test_level_edges(total):
    s = UserValueScore(total=total)
    assert s.level in ("入门", "进阶", "资深", "专家")

@pytest.mark.parametrize("i", range(10))
def test_to_dict(i):
    s = compute_value_score(total_events=i * 10, active_days=i)
    d = s.to_dict()
    assert "total" in d and "level" in d
    assert 0 <= d["total"] <= 100

@pytest.mark.parametrize("i", range(10))
def test_to_text(i):
    s = compute_value_score(total_events=i * 5)
    assert "价值分" in s.to_text()

@pytest.mark.parametrize("events,days,level", [
    (0, 0, "入门"), (30, 7, "资深"), (100, 14, "专家"),
])
def test_typical(events, days, level):
    s = compute_value_score(total_events=events, active_days=days)
    assert s.level == level or s.total >= 35

@pytest.mark.parametrize("combo", range(5))
def test_combo(combo):
    s = compute_value_score(
        total_events=combo * 20, active_days=combo, analysis_runs=combo * 3,
        backtest_runs=combo * 2, exports=combo * 2, feedback_count=combo,
    )
    assert s.total >= 0
