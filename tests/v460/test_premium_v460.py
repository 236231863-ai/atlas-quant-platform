"""v4.6 P6：商业化验证测试。

覆盖：Premium Feature Test / 解锁提示 / premium_view/click 埋点 / 免费vs会员。
"""
from __future__ import annotations

import pytest

from engine.premium import (
    PREMIUM_FEATURES, FeatureStatus, PremiumFeatureTest, premium_features,
)
from engine.user_analytics import AnalyticsTracker, EVENT_NAMES


# ---------- 功能列表 ----------
def test_features_count():
    assert len(PREMIUM_FEATURES) == 4


def test_features_include_expected():
    for f in ("自动兑奖提醒", "年度彩票报告", "无限历史保存", "家庭彩票管理"):
        assert f in PREMIUM_FEATURES


def test_free_locked():
    statuses = PremiumFeatureTest.features(is_premium=False)
    assert all(s.locked for s in statuses)


def test_premium_unlocked():
    statuses = PremiumFeatureTest.features(is_premium=True)
    assert all(not s.locked for s in statuses)


# ---------- FeatureStatus ----------
def test_feature_status_locked():
    s = FeatureStatus(name="自动兑奖提醒")
    assert s.locked is True
    assert "解锁" in s.unlock_text


def test_feature_status_unlocked():
    s = FeatureStatus(name="自动兑奖提醒", locked=False)
    assert s.locked is False
    assert s.unlock_text == ""


def test_feature_status_to_dict():
    s = FeatureStatus(name="年度彩票报告")
    d = s.to_dict()
    assert d["locked"] is True
    assert "解锁" in d["unlock_text"]


# ---------- 解锁提示 ----------
def test_locked_text():
    assert "升级 Atlas Premium 解锁" in PremiumFeatureTest.locked_text(False)


def test_locked_text_premium():
    assert PremiumFeatureTest.locked_text(True) == ""


def test_locked_text_contains_features():
    txt = PremiumFeatureTest.locked_text(False)
    assert "自动兑奖提醒" in txt
    assert "年度报告" in txt


# ---------- 埋点 ----------
def test_premium_events_in_names():
    assert "premium_view" in EVENT_NAMES
    assert "premium_click" in EVENT_NAMES


def test_view_records(ticket_storage):
    AnalyticsTracker().clear()
    PremiumFeatureTest.view("自动兑奖提醒")
    s = AnalyticsTracker().summary()
    assert s["premium_view"] == 1


def test_click_records(ticket_storage):
    AnalyticsTracker().clear()
    PremiumFeatureTest.click("年度彩票报告")
    s = AnalyticsTracker().summary()
    assert s["premium_click"] == 1


def test_view_metadata(ticket_storage):
    AnalyticsTracker().clear()
    PremiumFeatureTest.view("家庭彩票管理")
    evs = AnalyticsTracker().recent("premium_view", 1)
    assert evs[0].metadata.get("feature") == "家庭彩票管理"


# ---------- 便捷函数 ----------
def test_premium_features_helper():
    statuses = premium_features(False)
    assert len(statuses) == 4


def test_premium_features_premium():
    statuses = premium_features(True)
    assert all(not s.locked for s in statuses)


# ---------- 矩阵 ----------
@pytest.mark.parametrize("feature", list(PREMIUM_FEATURES))
def test_each_feature_locked(feature):
    s = PremiumFeatureTest.feature_status(feature, False)
    assert s.locked is True
    assert s.name == feature


@pytest.mark.parametrize("i", range(10))
def test_view_matrix(ticket_storage, i):
    AnalyticsTracker().clear()
    f = PREMIUM_FEATURES[i % 4]
    PremiumFeatureTest.view(f)
    assert AnalyticsTracker().count("premium_view") == 1
