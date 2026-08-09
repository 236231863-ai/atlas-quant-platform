"""v3.9.0 彩票量化智能分析层测试配置。"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (ROOT, os.path.join(ROOT, "desktop")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest


@pytest.fixture()
def task_storage(tmp_path, monkeypatch):
    """每个测试隔离的 PendingTask 存储目录（同时隔离 ATLAS_STORAGE_DIR，
    防止 TicketManager() 等引擎模块落到真实 ~/.atlas 误删用户数据）。"""
    monkeypatch.setenv("ATLAS_TASK_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)
