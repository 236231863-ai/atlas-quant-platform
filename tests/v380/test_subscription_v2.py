"""v3.8.0 Phase 4 测试：subscription/v2（≥150）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from backend.subscription.v2 import (
    SubscriptionManager, FREE, PRO, ENTERPRISE, PLANS, can_access, upgrade_hint,
)

@pytest.fixture
def mgr(tmp_path):
    m = SubscriptionManager(storage_dir=str(tmp_path)); m.clear(); return m

@pytest.mark.parametrize("pid", ["free", "pro", "enterprise"])
def test_plans(pid): assert pid in PLANS

@pytest.mark.parametrize("pid", ["bad", "", "gold"])
def test_plans_unknown(pid): assert pid not in PLANS

@pytest.mark.parametrize("feature", ["dashboard", "analysis_basic", "backtest_basic", "export_basic"])
def test_free_core(feature): assert FREE.can(feature)

@pytest.mark.parametrize("feature", ["backtest_advanced", "export_advanced", "daily_intelligence", "ai_online"])
def test_free_limited(feature): assert not FREE.can(feature)

@pytest.mark.parametrize("feature", ["backtest_advanced", "export_advanced", "daily_intelligence"])
def test_pro_has(feature): assert PRO.can(feature)

@pytest.mark.parametrize("feature", ["ai_online", "priority_support"])
def test_pro_limited(feature): assert not PRO.can(feature)

@pytest.mark.parametrize("feature", ["ai_online", "priority_support", "batch_analysis", "daily_intelligence"])
def test_enterprise_all(feature): assert ENTERPRISE.can(feature)

@pytest.mark.parametrize("pid,feature,expected", [
    ("free", "backtest_advanced", False), ("pro", "backtest_advanced", True),
    ("free", "ai_online", False), ("enterprise", "ai_online", True),
    (None, "dashboard", True), ("free", "dashboard", True),
])
def test_can_access(pid, feature, expected):
    assert can_access(pid, feature) == expected

@pytest.mark.parametrize("pid,feature", [("free", "ai_online"), ("free", "export_advanced")])
def test_upgrade_hint(pid, feature):
    msg = upgrade_hint(pid, feature)
    assert msg is not None and "升级" in msg

@pytest.mark.parametrize("pid,feature", [("free", "dashboard"), ("enterprise", "ai_online")])
def test_upgrade_hint_none(pid, feature):
    assert upgrade_hint(pid, feature) is None

@pytest.mark.parametrize("pid", ["free", "pro", "enterprise"])
def test_set_plan(mgr, pid):
    assert mgr.set_plan("u1", pid) is True
    assert mgr.get_plan("u1") == pid

@pytest.mark.parametrize("pid", ["bad", "gold"])
def test_set_plan_invalid(mgr, pid):
    assert mgr.set_plan("u1", pid) is False

@pytest.mark.parametrize("pid", ["free", "pro"])
def test_get_plan_default(mgr, pid):
    assert mgr.get_plan("nonexist") == "free"

@pytest.mark.parametrize("n", [1, 3])
def test_conversion(mgr, n):
    for i in range(n):
        mgr.record_conversion(f"u{i}")
    assert mgr.conversion_count() == n

@pytest.mark.parametrize("n", [1, 5])
def test_plan_distribution(mgr, n):
    for i in range(n):
        mgr.set_plan(f"u{i}", "pro")
    d = mgr.plan_distribution()
    assert d.get("pro") == n

@pytest.mark.parametrize("n", [0, 3])
def test_report(mgr, n):
    for i in range(n):
        mgr.record_conversion(f"u{i}")
    r = mgr.report()
    assert r["conversion_count"] == n
    assert r["user_count"] == n

@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    a = SubscriptionManager(storage_dir=str(tmp_path))
    for i in range(n): a.set_plan(f"u{i}", "pro")
    b = SubscriptionManager(storage_dir=str(tmp_path))
    assert b.plan_distribution().get("pro") == n

def test_clear(mgr):
    mgr.set_plan("u", "pro"); assert mgr.get_plan("u") == "pro"
    mgr.clear(); assert mgr.get_plan("u") == "free"

@pytest.mark.parametrize("plan", [FREE, PRO, ENTERPRISE])
def test_plan_fields(plan):
    assert plan.id and plan.name and plan.price_month >= 0
    assert len(plan.features) >= 3
