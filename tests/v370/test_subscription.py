"""v3.7.0 Phase 5 测试：Edition / FeatureFlag / 商业基础（≥100）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from backend.subscription import (
    Edition, COMMUNITY, PROFESSIONAL, RESEARCH, EDITIONS,
    get_edition, edition_features, FEATURES,
    FeatureFlag, can_use, gate,
)


# ---------- 版本定义 ----------
@pytest.mark.parametrize("edition", [COMMUNITY, PROFESSIONAL, RESEARCH])
def test_edition_defined(edition):
    assert edition.id
    assert edition.name
    assert edition.features


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_editions_registry(eid):
    assert eid in EDITIONS


@pytest.mark.parametrize("eid", ["", "none", "enterprise", "gold"])
def test_editions_unknown(eid):
    assert get_edition(eid) is None


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_get_edition(eid):
    assert get_edition(eid).id == eid


# ---------- 版本功能矩阵 ----------
@pytest.mark.parametrize("feature", ["dashboard", "analysis_basic", "backtest_basic", "export_basic", "data_full"])
def test_community_core_features(feature):
    assert COMMUNITY.has(feature)


@pytest.mark.parametrize("feature", ["analysis_advanced", "backtest_advanced", "export_advanced", "daily_intelligence", "ai_online", "priority_support"])
def test_community_limited(feature):
    assert not COMMUNITY.has(feature)


@pytest.mark.parametrize("feature", ["dashboard", "analysis_advanced", "backtest_advanced", "export_advanced", "daily_intelligence"])
def test_professional_has(feature):
    assert PROFESSIONAL.has(feature)


@pytest.mark.parametrize("feature", ["ai_online", "priority_support"])
def test_professional_not_has(feature):
    assert not PROFESSIONAL.has(feature)


@pytest.mark.parametrize("feature", ["dashboard", "backtest_advanced", "ai_online", "priority_support", "export_advanced"])
def test_research_has_all(feature):
    assert RESEARCH.has(feature)


# ---------- 版本功能数量 ----------
@pytest.mark.parametrize("eid,count", [
    ("community", len(COMMUNITY.features)),
    ("professional", len(PROFESSIONAL.features)),
    ("research", len(RESEARCH.features)),
])
def test_edition_feature_count(eid, count):
    assert len(edition_features(eid)) == count


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_edition_features_nonempty(eid):
    assert len(edition_features(eid)) > 0


@pytest.mark.parametrize("eid", ["unknown"])
def test_edition_features_unknown(eid):
    assert edition_features(eid) == []


# ---------- FeatureFlag ----------
@pytest.mark.parametrize("eid", ["community", "professional", "research", None, "unknown"])
def test_current_edition_fallback(eid):
    ed = FeatureFlag.current_edition(eid)
    assert ed.id in ("community", "professional", "research")


@pytest.mark.parametrize("eid,feature,expected", [
    ("community", "dashboard", True),
    ("community", "ai_online", False),
    ("professional", "ai_online", False),
    ("research", "ai_online", True),
    (None, "dashboard", True),
    ("unknown", "backtest_basic", True),
])
def test_can_use(eid, feature, expected):
    assert can_use(eid, feature) == expected


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_can_use_dashboard(eid):
    assert can_use(eid, "dashboard")


@pytest.mark.parametrize("eid", ["community", "professional"])
def test_can_use_priority(eid):
    assert not can_use(eid, "priority_support")


# ---------- 升级提示 ----------
@pytest.mark.parametrize("feature", ["ai_online", "priority_support", "export_advanced"])
def test_gate_community(feature):
    msg = gate("community", feature)
    assert msg is not None
    assert "升级" in msg


@pytest.mark.parametrize("feature", ["dashboard", "backtest_basic"])
def test_gate_community_allowed(feature):
    assert gate("community", feature) is None


@pytest.mark.parametrize("eid", ["professional", "research"])
@pytest.mark.parametrize("feature", ["dashboard", "backtest_advanced"])
def test_gate_higher_editions(eid, feature):
    assert gate(eid, feature) is None


@pytest.mark.parametrize("eid", ["community", "professional"])
def test_gate_priority_higher(eid):
    msg = gate(eid, "priority_support")
    if eid == "research":
        assert msg is None
    else:
        assert msg is not None


# ---------- 可用功能列表 ----------
@pytest.mark.parametrize("eid,expected_has", [
    ("community", "analysis_basic"),
    ("professional", "daily_intelligence"),
    ("research", "ai_online"),
])
def test_available_features(eid, expected_has):
    feats = FeatureFlag.available_features(eid)
    assert expected_has in feats


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_available_features_count(eid):
    assert len(FeatureFlag.available_features(eid)) > 0


# ---------- 功能字典 ----------
@pytest.mark.parametrize("feature", ["dashboard", "analysis_basic", "export_advanced", "daily_intelligence", "ai_online"])
def test_feature_labels(feature):
    assert feature in FEATURES
    assert FEATURES[feature]


# ---------- 版本升级关系 ----------
@pytest.mark.parametrize("feature", ["analysis_advanced", "backtest_advanced", "export_advanced", "daily_intelligence"])
def test_upgrade_progression(feature):
    # Community 无 → Professional/Research 有
    assert not COMMUNITY.has(feature)
    assert PROFESSIONAL.has(feature)
    assert RESEARCH.has(feature)


@pytest.mark.parametrize("feature", ["ai_online", "priority_support"])
def test_research_exclusive(feature):
    assert not COMMUNITY.has(feature)
    assert not PROFESSIONAL.has(feature)
    assert RESEARCH.has(feature)


# ---------- 描述字段 ----------
@pytest.mark.parametrize("edition", [COMMUNITY, PROFESSIONAL, RESEARCH])
def test_edition_description(edition):
    assert edition.description
    assert edition.price_label


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_price_label(eid):
    assert EDITIONS[eid].price_label


# ---------- 补充：边界 ----------
@pytest.mark.parametrize("edition", [COMMUNITY, PROFESSIONAL, RESEARCH])
def test_edition_has_method(edition):
    assert edition.has("dashboard") is True
    assert edition.missing("dashboard") is False


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_edition_roundtrip(eid):
    ed = get_edition(eid)
    assert EDITIONS[ed.id] is ed


@pytest.mark.parametrize("feature", list(FEATURES.keys()))
def test_feature_key_valid(feature):
    assert feature in FEATURES


@pytest.mark.parametrize("eid", ["community", "professional", "research"])
def test_gate_dashboard_none(eid):
    assert gate(eid, "dashboard") is None


@pytest.mark.parametrize("eid", [None, ""])
def test_gate_none_fallback(eid):
    assert gate(eid, "dashboard") is None
    assert gate(eid, "ai_online") is not None
