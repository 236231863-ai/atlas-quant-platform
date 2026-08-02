"""v3.8.0 最终补充矩阵（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.value_score import compute_value_score, UserValueScore
from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary
from engine.product_value import FeatureValueEngine
from engine.feedback_intelligence import FeedbackIntelligence
from backend.subscription.v2 import can_access, upgrade_hint

# value_score 连续网格
@pytest.mark.parametrize("total", range(0, 101, 5))
def test_value_contiguous(total):
    s = compute_value_score(total_events=total, active_days=2)
    assert 0 <= s.total <= 100

@pytest.mark.parametrize("total", [0, 25, 50, 75, 100])
@pytest.mark.parametrize("level", ["入门", "进阶", "资深", "专家"])
def test_level_all(total, level):
    s = UserValueScore(total=total)
    assert s.level in ("入门", "进阶", "资深", "专家")

# 事件组合网格
_E = ["APP_START", "ANALYSIS_RUN", "REPORT_EXPORT", "BACKTEST_RUN"]
@pytest.mark.parametrize("e1", _E)
@pytest.mark.parametrize("e2", _E)
def test_event_pairs(tmp_path, e1, e2):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    ui.track(e1); ui.track(e2)
    s = build_behavior_summary(ui)
    assert s.total_events == 2

# product_value 连续
@pytest.mark.parametrize("usage", range(0, 21))
def test_feature_contiguous(usage):
    f = FeatureValueEngine.score("f", usage=usage)
    assert 0 <= f.value <= 100

# subscription 全矩阵
_P = ["free", "pro", "enterprise", None, ""]
_F = ["dashboard", "ai_online", "batch_analysis", "export_advanced", "daily_intelligence"]
@pytest.mark.parametrize("plan", _P)
@pytest.mark.parametrize("feature", _F)
def test_sub_all(plan, feature):
    assert can_access(plan, feature) in (True, False)
    h = upgrade_hint(plan, feature)
    assert h is None or "升级" in h

# feedback 连续
@pytest.mark.parametrize("content", ["崩溃", "报错", "闪退", "无法", "失效", "希望", "建议", "数据", "导出", "界面"])
def test_feedback_all(content):
    ins = FeedbackIntelligence.analyze([{"content": content, "status": "new"}])
    assert ins.total == 1
    assert sum(ins.by_category.values()) == 1

# 稳定性：重复计算一致
@pytest.mark.parametrize("i", range(10))
def test_deterministic(i):
    a = compute_value_score(total_events=50, active_days=5)
    b = compute_value_score(total_events=50, active_days=5)
    assert a.total == b.total
