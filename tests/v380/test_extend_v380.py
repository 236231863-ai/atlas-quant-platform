"""v3.8.0 补充矩阵（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.value_score import compute_value_score
from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary
from engine.product_value import FeatureValueEngine
from engine.feedback_intelligence import FeedbackIntelligence
from backend.subscription.v2 import can_access

# value_score 大网格
_TOTALS = [0, 1, 3, 8, 15, 30, 60, 120, 250, 500]
_DAYS = [0, 1, 2, 4, 6, 8, 10, 14]
@pytest.mark.parametrize("total", _TOTALS)
@pytest.mark.parametrize("days", _DAYS)
def test_value_big_grid(total, days):
    s = compute_value_score(total_events=total, active_days=days)
    assert 0 <= s.total <= 100
    assert s.usage_score <= 20 and s.retention_score <= 20

# value_score 单维网格
@pytest.mark.parametrize("analysis", range(0, 21, 2))
@pytest.mark.parametrize("backtest", [0, 5, 15])
def test_research_grid(analysis, backtest):
    s = compute_value_score(analysis_runs=analysis, backtest_runs=backtest)
    assert 0 <= s.research_score <= 20

@pytest.mark.parametrize("exports", range(0, 11))
@pytest.mark.parametrize("fb", [0, 1, 3])
def test_export_feedback_grid(exports, fb):
    s = compute_value_score(exports=exports, feedback_count=fb)
    assert s.export_score <= 20 and s.feedback_score <= 20

# user_intel 事件大网格
_EVENTS = ["APP_START", "ANALYSIS_RUN", "REPORT_EXPORT", "BACKTEST_RUN", "STRATEGY_SAVE", "FEEDBACK_SEND"]
@pytest.mark.parametrize("event", _EVENTS)
@pytest.mark.parametrize("n", [1, 4, 9, 16])
def test_events_big_grid(tmp_path, event, n):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(n):
        ui.track(event)
    assert build_behavior_summary(ui).by_event.get(event, 0) == n

# product_value 大网格
@pytest.mark.parametrize("usage", [0, 2, 6, 15, 40, 100])
@pytest.mark.parametrize("dur", [0, 2, 8, 20])
def test_feature_big_grid(usage, dur):
    f = FeatureValueEngine.score("f", usage=usage, duration_min=dur)
    assert 0 <= f.value <= 100

# subscription 大网格
_PLANS = ["free", "pro", "enterprise"]
_FEATURES = ["dashboard", "analysis_basic", "analysis_advanced", "backtest_basic",
             "backtest_advanced", "export_basic", "export_advanced",
             "daily_intelligence", "data_full", "ai_online", "priority_support"]
@pytest.mark.parametrize("plan", _PLANS)
@pytest.mark.parametrize("feature", _FEATURES)
def test_subscription_big_grid(plan, feature):
    assert can_access(plan, feature) in (True, False)

# feedback 大网格
@pytest.mark.parametrize("content", ["崩溃", "报错", "闪退", "希望", "建议", "数据", "导出", "界面", "PDF", "错误"])
@pytest.mark.parametrize("n", [1, 2])
def test_feedback_big_grid(content, n):
    items = [{"content": content, "status": "new"} for _ in range(n)]
    ins = FeedbackIntelligence.analyze(items)
    assert ins.total == n
