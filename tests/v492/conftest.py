"""v492 Mobile MVP 测试 conftest。

隔离策略：
  - MobileDB 使用 in-memory（:memory:），不触碰真实 ~/.atlas
  - ATLAS_STORAGE_DIR 指向 tmp_path，防止 user_experiment 写真实数据
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.mobile.db import MobileDB  # noqa: E402
from backend.mobile.service import MobileService  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_storage(tmp_path, monkeypatch):
    """隔离 user_experiment 存储目录。"""
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    yield


@pytest.fixture
def db():
    """in-memory MobileDB。"""
    return MobileDB.in_memory()


@pytest.fixture
def service(db):
    """MobileService（绑定 in-memory db 的 session）。"""
    return MobileService(db.session())


@pytest.fixture
def svc_session(db):
    return db.session()
