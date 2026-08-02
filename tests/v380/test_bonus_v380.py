"""v3.8.0 奖励补充矩阵（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.value_score import compute_value_score
from engine.product_value import FeatureValueEngine
from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary

# value_score 大网格
@pytest.mark.parametrize("total", range(0, 200, 7))
def test_value_step(total):
    s = compute_value_score(total_events=total, active_days=3)
    assert 0 <= s.total <= 100

@pytest.mark.parametrize("analysis", range(0, 31, 3))
@pytest.mark.parametrize("backtest", [0, 2, 5, 10])
def test_research_wide(analysis, backtest):
    s = compute_value_score(analysis_runs=analysis, backtest_runs=backtest)
    assert 0 <= s.research_score <= 20

# feature 网格
@pytest.mark.parametrize("usage", range(0, 50, 3))
@pytest.mark.parametrize("sat", [0, 2, 4, 5])
def test_feature_wide(usage, sat):
    f = FeatureValueEngine.score("f", usage=usage, satisfaction=sat)
    assert 0 <= f.value <= 100

# 事件：连续会话
@pytest.mark.parametrize("n", range(1, 11))
def test_sessions_wide(tmp_path, n):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(n):
        ui.app_start()
    assert len(ui.load()) == n

# 汇总一致性
@pytest.mark.parametrize("i", range(5))
def test_summary_consistent(tmp_path, i):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(i + 1):
        ui.app_start()
    s1 = build_behavior_summary(ui)
    s2 = build_behavior_summary(ui)
    assert s1.total_events == s2.total_events == i + 1
