"""v4.2 User Growth & Data Flywheel Sprint 测试配置。"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (ROOT, os.path.join(ROOT, "desktop")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest


@pytest.fixture()
def ticket_storage(tmp_path, monkeypatch):
    """通过 ATLAS_STORAGE_DIR 隔离存储（不 monkeypatch os.path.expanduser，
    以免破坏 matplotlib 首次加载 matplotlibrc 的 expanduser 调用）。"""
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("ATLAS_TASK_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)
