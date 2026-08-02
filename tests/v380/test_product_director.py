"""v3.8.0 Phase 6 测试：product_director_v2（≥150）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.intelligence.product_director_v2 import ProductDirectorV2, ProductAssessment

@pytest.mark.parametrize("kwargs", [
    {}, {"total_events": 10}, {"active_days": 3},
    {"analysis_runs": 5, "exports": 2}, {"crash_rate": 0.1},
    {"feedback_items": [{"content": "崩溃", "status": "new"}]},
])
def test_assess_default(kwargs):
    a = ProductDirectorV2.assess(**kwargs)
    assert 0 <= a.health_score <= 100

@pytest.mark.parametrize("crash", [0.0, 0.05, 0.1, 0.5])
def test_crash_health(crash):
    a = ProductDirectorV2.assess(crash_rate=crash)
    if crash > 0.05:
        assert any("崩溃" in i for i in a.issues)

@pytest.mark.parametrize("completion", [0.0, 0.5, 0.8])
def test_completion_health(completion):
    a = ProductDirectorV2.assess(analysis_runs=10, analysis_completion=completion)
    if completion < 0.6:
        assert any("完成率" in i for i in a.issues)

@pytest.mark.parametrize("n_bugs", [0, 3, 5])
def test_bug_feedback_health(n_bugs):
    items = [{"content": "崩溃", "status": "new"} for _ in range(n_bugs)]
    a = ProductDirectorV2.assess(feedback_items=items)
    if n_bugs >= 3:
        assert any("Bug" in i for i in a.issues)

@pytest.mark.parametrize("days", [0, 2, 7])
def test_active_days_health(days):
    a = ProductDirectorV2.assess(active_days=days)
    if days < 3:
        assert any("活跃度" in i for i in a.issues)

@pytest.mark.parametrize("exports", [0, 3])
def test_roadmap_exports(exports):
    a = ProductDirectorV2.assess(exports=exports)
    if exports == 0:
        assert any("导出" in r for r in a.roadmap)

@pytest.mark.parametrize("backtests", [0, 3])
def test_roadmap_backtest(backtests):
    a = ProductDirectorV2.assess(backtest_runs=backtests)
    if backtests == 0:
        assert any("回测" in r for r in a.roadmap)

@pytest.mark.parametrize("items", [[], [{"content": "崩溃", "status": "new"}]])
def test_feedback_insight(items):
    a = ProductDirectorV2.assess(feedback_items=items)
    assert a.feedback_insight.total == len(items)

@pytest.mark.parametrize("i", range(10))
def test_health_bounds(i):
    a = ProductDirectorV2.assess(total_events=i * 20, active_days=i % 7, exports=i)
    assert 0 <= a.health_score <= 100
    assert 0 <= a.user_value.total <= 100

@pytest.mark.parametrize("n", [0, 5])
def test_to_text(n):
    a = ProductDirectorV2.assess(total_events=n)
    text = a.to_text()
    assert "产品评估" in text

@pytest.mark.parametrize("i", range(5))
def test_roadmap_nonempty_when_issues(i):
    a = ProductDirectorV2.assess(crash_rate=0.2, analysis_runs=5, analysis_completion=0.3)
    assert len(a.roadmap) >= 1
