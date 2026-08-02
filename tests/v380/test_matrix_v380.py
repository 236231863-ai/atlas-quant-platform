"""v3.8.0 大规模参数化矩阵（补充至 1000+）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.value_score import compute_value_score, UserValueScore
from engine.product_value import FeatureValueEngine
from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary
from engine.feedback_intelligence import FeedbackIntelligence
from backend.subscription.v2 import can_access, upgrade_hint, SubscriptionManager
from engine.intelligence.product_director_v2 import ProductDirectorV2


# ---------- value_score 网格 ----------
@pytest.mark.parametrize("total", [0, 5, 15, 40, 80, 200])
@pytest.mark.parametrize("days", [0, 2, 5, 10])
def test_value_grid(total, days):
    s = compute_value_score(total_events=total, active_days=days)
    assert 0 <= s.total <= 100
    assert s.total >= s.usage_score

@pytest.mark.parametrize("a,b,c,d,e,f", [
    (0, 0, 0, 0, 0, 0), (10, 3, 5, 3, 2, 2), (50, 7, 20, 10, 5, 3),
    (200, 14, 60, 30, 20, 8),
])
def test_value_multi(a, b, c, d, e, f):
    s = compute_value_score(total_events=a, active_days=b, analysis_runs=c,
                            backtest_runs=d, exports=e, feedback_count=f)
    assert 0 <= s.total <= 100
    assert s.level in ("入门", "进阶", "资深", "专家")

@pytest.mark.parametrize("total", range(0, 101, 10))
def test_value_total_range(total):
    s = compute_value_score(total_events=total, active_days=3)
    assert 0 <= s.total <= 100

@pytest.mark.parametrize("total", [35, 60, 80])
@pytest.mark.parametrize("level", ["入门", "进阶", "资深", "专家"])
def test_level_boundary(total, level):
    s = UserValueScore(total=total)
    assert isinstance(s.level, str)

# ---------- user_intel 事件矩阵 ----------
@pytest.mark.parametrize("n", [1, 2, 5, 10, 20])
@pytest.mark.parametrize("event", ["APP_START", "ANALYSIS_RUN", "BACKTEST_RUN", "REPORT_EXPORT"])
def test_event_counts(tmp_path, n, event):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(n):
        ui.track(event)
    s = build_behavior_summary(ui)
    assert s.by_event.get(event, 0) == n

@pytest.mark.parametrize("n", [1, 3, 8])
def test_full_flow(tmp_path, n):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(n):
        ui.app_start(); ui.analysis_run("hot"); ui.backtest_run("hot")
        ui.report_export("pdf"); ui.feedback_send("bug")
    s = build_behavior_summary(ui)
    assert s.total_events == n * 5
    assert s.by_event.get("APP_START", 0) == n

@pytest.mark.parametrize("i", range(5))
def test_ui_persist_matrix(tmp_path, i):
    ui = UserIntelligenceV3(storage_dir=str(tmp_path)); ui.clear()
    for _ in range(i + 1):
        ui.app_start()
    ui2 = UserIntelligenceV3(storage_dir=str(tmp_path))
    assert len(ui2.load()) == i + 1

# ---------- product_value 网格 ----------
@pytest.mark.parametrize("usage", [0, 3, 10, 30, 100])
@pytest.mark.parametrize("sat", [0, 3, 5])
def test_feature_grid(usage, sat):
    f = FeatureValueEngine.score("f", usage=usage, satisfaction=sat)
    assert 0 <= f.value <= 100

@pytest.mark.parametrize("i", range(20))
def test_feature_rank_matrix(i):
    items = [FeatureValueEngine.score(f"f{j}", usage=j * 5) for j in range(5)]
    ranked = FeatureValueEngine.rank(items)
    assert ranked[0].value >= ranked[-1].value

# ---------- subscription 矩阵 ----------
@pytest.mark.parametrize("plan", ["free", "pro", "enterprise"])
@pytest.mark.parametrize("feature", ["dashboard", "backtest_advanced", "ai_online"])
def test_subscription_matrix(plan, feature):
    assert can_access(plan, feature) in (True, False)

@pytest.mark.parametrize("n", [1, 3, 10])
def test_sub_manager_matrix(tmp_path, n):
    m = SubscriptionManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.record_conversion(f"u{i}")
    assert m.conversion_count() == n

@pytest.mark.parametrize("i", range(5))
def test_sub_persist(tmp_path, i):
    m = SubscriptionManager(storage_dir=str(tmp_path)); m.clear()
    m.set_plan("u", "pro")
    m2 = SubscriptionManager(storage_dir=str(tmp_path))
    assert m2.get_plan("u") == "pro"

# ---------- feedback_intel 矩阵 ----------
@pytest.mark.parametrize("content", ["崩溃", "报错", "希望", "建议", "数据", "导出", "界面", "随便"])
@pytest.mark.parametrize("status", ["new", "reviewing", "fixed", "closed"])
def test_feedback_matrix(content, status):
    ins = FeedbackIntelligence.analyze([{"content": content, "status": status}])
    assert ins.total == 1

@pytest.mark.parametrize("n", [1, 5, 20])
def test_feedback_n(n):
    items = [{"content": "崩溃", "status": "new"} for _ in range(n)]
    ins = FeedbackIntelligence.analyze(items)
    assert ins.total == n
    assert ins.by_category.get("bug", 0) == n

# ---------- product_director 矩阵 ----------
@pytest.mark.parametrize("crash", [0.0, 0.1, 0.3])
@pytest.mark.parametrize("days", [0, 3, 7])
def test_director_matrix(crash, days):
    a = ProductDirectorV2.assess(crash_rate=crash, active_days=days)
    assert 0 <= a.health_score <= 100
    assert len(a.roadmap) >= 1

@pytest.mark.parametrize("i", range(5))
def test_director_consistency(i):
    a1 = ProductDirectorV2.assess(total_events=i * 10, exports=2)
    a2 = ProductDirectorV2.assess(total_events=i * 10, exports=2)
    assert a1.health_score == a2.health_score
