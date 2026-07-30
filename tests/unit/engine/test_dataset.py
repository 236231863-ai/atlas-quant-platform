"""Tests for Dataset Versioning System."""
from __future__ import annotations
import pytest
from engine.dataset import DatasetRegistry, DatasetRecord

class TestDatasetRegistry:
    def test_empty(self):
        r = DatasetRegistry(); assert r.count() == 0
    def test_register(self):
        r = DatasetRegistry()
        d = DatasetRecord("d1","1.0","csv","abc123",["f1","f2"])
        r.register(d); assert r.count() == 1
    def test_get(self):
        r = DatasetRegistry()
        d = DatasetRecord("d1","1.0","csv","abc123",["f1"])
        r.register(d); assert r.get("d1") is not None
    def test_get_nonexistent(self):
        assert DatasetRegistry().get("nonexistent") is None
    def test_list(self):
        r = DatasetRegistry()
        r.register(DatasetRecord("d1","1","csv","h1",["f1"]))
        r.register(DatasetRecord("d2","1","api","h2",["f1","f2"]))
        assert len(r.list()) == 2
    def test_compare_identical(self):
        r = DatasetRegistry()
        r.register(DatasetRecord("d1","1","csv","h",["f1"]))
        r.register(DatasetRecord("d2","1","csv","h",["f1"]))
        c = r.compare("d1","d2")
        assert c["same_version"] and c["same_hash"]
    def test_compare_different(self):
        r = DatasetRegistry()
        r.register(DatasetRecord("d1","1","csv","h1",["f1"]))
        r.register(DatasetRecord("d2","2","api","h2",["f2"]))
        c = r.compare("d1","d2")
        assert not c["same_version"]
    def test_compare_not_found(self):
        r = DatasetRegistry()
        r.register(DatasetRecord("d1","1","csv","h",["f1"]))
        c = r.compare("d1","nonexistent")
        assert "error" in c
    def test_compute_hash(self):
        h = DatasetRegistry.compute_hash({"a":1,"b":2})
        assert len(h) == 16
