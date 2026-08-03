"""v4.2 Phase 5：Atlas Premium 会员体系测试。"""
from __future__ import annotations

import os

import pytest

from engine.premium import (
    FEATURES,
    PLAN_FREE,
    PLAN_PREMIUM,
    PremiumFeature,
    PremiumManager,
    PremiumPlan,
    feature_matrix,
)


# ---------- 功能定义 ----------
def test_feature_count():
    assert len(FEATURES) >= 8


def test_required_premium_features():
    keys = {f.key for f in FEATURES}
    for k in ("auto_remind", "unlimited_history", "annual_report", "advanced_review"):
        assert k in keys
    assert FEATURES and all(f.tier == PLAN_PREMIUM for f in FEATURES if f.key in
                            ("auto_remind", "unlimited_history", "annual_report", "advanced_review"))


def test_free_features():
    keys = {f.key for f in FEATURES if f.tier == PLAN_FREE}
    assert "basic_claim" in keys
    assert "auto_remind" not in keys


def test_feature_tiers_valid():
    for f in FEATURES:
        assert f.tier in (PLAN_FREE, PLAN_PREMIUM)
        assert isinstance(f.key, str) and f.key
        assert isinstance(f.name, str) and f.name
        assert isinstance(f.description, str)


def test_feature_keys_unique():
    keys = [f.key for f in FEATURES]
    assert len(keys) == len(set(keys))


def test_get_feature():
    f = PremiumPlan.get_feature("annual_report")
    assert f is not None
    assert f.name == "年度报告"


def test_get_feature_missing():
    assert PremiumPlan.get_feature("nonexistent") is None


# ---------- 权限 ----------
def test_free_entitlements():
    e = PremiumPlan.entitlements(PLAN_FREE)
    assert "basic_claim" in e
    for k in ("auto_remind", "unlimited_history", "annual_report", "advanced_review"):
        assert k not in e


def test_premium_entitlements_superset():
    free = set(PremiumPlan.entitlements(PLAN_FREE))
    prem = set(PremiumPlan.entitlements(PLAN_PREMIUM))
    assert free < prem  # 会员包含免费全部 + 会员功能


def test_premium_entitlements():
    e = PremiumPlan.entitlements(PLAN_PREMIUM)
    for k in ("auto_remind", "unlimited_history", "annual_report", "advanced_review",
              "basic_claim", "ticket_save"):
        assert k in e


@pytest.mark.parametrize("feature", ["auto_remind", "unlimited_history", "annual_report", "advanced_review"])
def test_is_entitled_premium_only(feature):
    assert PremiumPlan.is_entitled(PLAN_FREE, feature) is False
    assert PremiumPlan.is_entitled(PLAN_PREMIUM, feature) is True


@pytest.mark.parametrize("feature", ["basic_claim", "ticket_save", "budget_center", "health_index"])
def test_is_entitled_free_ok(feature):
    assert PremiumPlan.is_entitled(PLAN_FREE, feature) is True
    assert PremiumPlan.is_entitled(PLAN_PREMIUM, feature) is True


@pytest.mark.parametrize("tier", [PLAN_FREE, PLAN_PREMIUM])
def test_entitlements_all_exist(tier):
    for k in PremiumPlan.entitlements(tier):
        assert PremiumPlan.get_feature(k) is not None


# ---------- tier_name ----------
def test_tier_name():
    assert PremiumPlan.tier_name(PLAN_FREE) == "免费版"
    assert PremiumPlan.tier_name(PLAN_PREMIUM) == "Atlas Premium"
    assert PremiumPlan.tier_name("x") == "x"


# ---------- 红线：不卖预测 ----------
def test_no_prediction_features():
    for f in FEATURES:
        assert "预测" not in f.name
        assert "预测" not in f.description
        assert "选号" not in f.name
        assert "提高中奖" not in f.description
        assert "稳赚" not in f.description


def test_pricing_no_prediction():
    p = PremiumPlan.pricing_hint()
    # 政策明确声明不卖预测
    assert "不包含任何预测功能" in p["policy"]
    for bad in ("预测中奖", "预测号码", "稳赚", "必中", "提高中奖"):
        assert bad not in p["policy"]


def test_feature_matrix():
    rows = feature_matrix()
    assert len(rows) == len(FEATURES)
    premium_rows = [r for r in rows if r["premium"]]
    assert len(premium_rows) == len(FEATURES)
    free_only = {r["key"] for r in rows if r["free"]}
    assert "basic_claim" in free_only


# ---------- PremiumManager ----------
def test_manager_default_free(ticket_storage):
    m = PremiumManager()
    assert m.get_tier() == PLAN_FREE
    assert m.is_premium() is False


def test_manager_set_premium(ticket_storage):
    m = PremiumManager()
    m.set_tier(PLAN_PREMIUM)
    assert m.is_premium() is True
    assert m.get_tier() == PLAN_PREMIUM


def test_manager_set_invalid_falls_back(ticket_storage):
    m = PremiumManager()
    m.set_tier("hacker")
    assert m.get_tier() == PLAN_FREE


def test_manager_persist(ticket_storage):
    m1 = PremiumManager()
    m1.set_tier(PLAN_PREMIUM)
    m2 = PremiumManager()
    assert m2.is_premium() is True


def test_manager_gate_free(ticket_storage):
    m = PremiumManager()
    assert m.is_allowed("basic_claim") is True
    assert m.is_allowed("annual_report") is False
    assert m.is_allowed("auto_remind") is False


def test_manager_gate_premium(ticket_storage):
    m = PremiumManager()
    m.set_tier(PLAN_PREMIUM)
    assert m.is_allowed("annual_report") is True
    assert m.is_allowed("auto_remind") is True
    assert m.is_allowed("basic_claim") is True


@pytest.mark.parametrize("tier", [PLAN_FREE, PLAN_PREMIUM])
@pytest.mark.parametrize("feature", ["basic_claim", "auto_remind", "annual_report", "advanced_review",
                                     "unlimited_history", "ticket_save", "budget_center", "health_index"])
def test_gate_matrix(tier, feature, ticket_storage):
    m = PremiumManager()
    m.set_tier(tier)
    assert m.is_allowed(feature) == PremiumPlan.is_entitled(tier, feature)


# ---------- 数据服务导向 ----------
def test_premium_are_data_services():
    """会员功能全部是数据服务，非预测。"""
    for k in ("auto_remind", "unlimited_history", "annual_report", "advanced_review"):
        f = PremiumPlan.get_feature(k)
        assert f.tier == PLAN_PREMIUM
        assert any(word in f.description for word in ("提醒", "历史", "报告", "复盘"))


# ---------- to_dict ----------
def test_feature_to_dict():
    f = PremiumFeature("x", "X", PLAN_FREE, "desc")
    d = f.to_dict()
    assert d == {"key": "x", "name": "X", "tier": PLAN_FREE, "description": "desc"}
