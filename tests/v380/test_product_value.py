"""v3.8.0 Phase 3 测试：product_value（≥150）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.product_value import FeatureValueEngine, analyze_features

@pytest.mark.parametrize("usage", [0, 5, 20, 50, 100])
def test_usage_contribution(usage):
    f = FeatureValueEngine.score("f", usage=usage)
    assert 0 <= f.value <= 100

@pytest.mark.parametrize("dur", [0, 3, 10, 30])
def test_duration_contribution(dur):
    f = FeatureValueEngine.score("f", duration_min=dur)
    assert f.duration_min == dur

@pytest.mark.parametrize("sat", [0, 3, 5])
def test_satisfaction(sat):
    f = FeatureValueEngine.score("f", satisfaction=sat)
    assert f.satisfaction == sat

@pytest.mark.parametrize("conv", [0, 0.5, 1.0])
def test_conversion(conv):
    f = FeatureValueEngine.score("f", conversion=conv)
    assert f.conversion == conv

@pytest.mark.parametrize("features", [
    [{"feature": "a", "usage": 10}],
    [{"feature": "b", "usage": 20, "duration_min": 5}],
    [{"feature": "c", "usage": 5, "satisfaction": 4, "conversion": 0.3}],
])
def test_analyze_features(features):
    res = analyze_features(features)
    assert len(res) == len(features)
    assert all(0 <= x.value <= 100 for x in res)

@pytest.mark.parametrize("n", [1, 3, 5])
def test_rank(n):
    items = [FeatureValueEngine.score(f"f{i}", usage=i * 10) for i in range(n)]
    ranked = FeatureValueEngine.rank(items)
    assert all(ranked[i].value >= ranked[i + 1].value for i in range(len(ranked) - 1))

@pytest.mark.parametrize("f", [FeatureValueEngine.score("x", usage=i * 5) for i in range(10)])
def test_value_bounds(f):
    assert 0 <= f.value <= 100
    assert f.feature

@pytest.mark.parametrize("i", range(10))
def test_to_dict(i):
    f = FeatureValueEngine.score("f", usage=i * 10)
    d = f.to_dict()
    assert d["feature"] == "f"
    assert "value" in d

@pytest.mark.parametrize("kwargs", [
    {"feature": "a"}, {"feature": "b", "usage": 5},
    {"feature": "c", "duration_min": 3, "satisfaction": 4},
])
def test_score_minimal(kwargs):
    f = FeatureValueEngine.score(**kwargs)
    assert f.value >= 0
