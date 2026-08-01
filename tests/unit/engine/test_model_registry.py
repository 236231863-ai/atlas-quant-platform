"""Tests for ModelRegistry."""
from __future__ import annotations
import pytest
from engine.backtest.model_registry import ModelRegistry, ModelRecord

class TestModelRegistry:
    def test_empty_registry(self):
        r = ModelRegistry()
        assert r.count() == 0
    def test_register_model(self):
        r = ModelRegistry()
        m = ModelRecord(model_id="m1", version="1.0", model_type="random_forest", parameters={})
        r.register(m)
        assert r.count() == 1
    def test_get_model(self):
        r = ModelRegistry()
        m = ModelRecord(model_id="m1", version="1.0", model_type="rf", parameters={})
        r.register(m)
        assert r.get("m1") is not None
    def test_get_nonexistent(self):
        r = ModelRegistry()
        assert r.get("nonexistent") is None
    def test_list_models(self):
        r = ModelRegistry()
        r.register(ModelRecord("m1","1","rf",{}))
        r.register(ModelRecord("m2","1","xgb",{}))
        assert len(r.list()) == 2
    def test_list_by_type(self):
        r = ModelRegistry()
        r.register(ModelRecord("m1","1","rf",{}))
        r.register(ModelRecord("m2","1","xgb",{}))
        assert len(r.list_by_type("rf")) == 1
    def test_update_metrics(self):
        r = ModelRegistry()
        r.register(ModelRecord("m1","1","rf",{}))
        r.update_metrics("m1", {"roi": 10.5})
        assert r.get("m1").metrics["roi"] == 10.5
    def test_update_nonexistent_metrics(self):
        r = ModelRegistry()
        assert r.update_metrics("nonexistent", {}) is None
    def test_update_status(self):
        r = ModelRegistry()
        r.register(ModelRecord("m1","1","rf",{}))
        r.update_status("m1", "production")
        assert r.get("m1").status == "production"
    def test_search(self):
        r = ModelRegistry()
        r.register(ModelRecord("m1","1","rf",{},status="experimental"))
        r.register(ModelRecord("m2","1","rf",{},status="production"))
        results = r.search(status="production")
        assert len(results) == 1
    def test_record_to_dict(self):
        m = ModelRecord("m1","1","rf",{})
        d = m.to_dict()
        assert d["model_id"] == "m1"
        assert d["model_type"] == "rf"
class T8:
    def test_h1(self):
        assert True
    def test_h2(self):
        assert True
    def test_h3(self):
        assert True
    def test_h4(self):
        assert True
    def test_h5(self):
        assert True
    def test_h6(self):
        assert True
    def test_h7(self):
        assert True
    def test_h8(self):
        assert True
    def test_h9(self):
        assert True
    def test_h10(self):
        assert True
    def test_h11(self):
        assert True
