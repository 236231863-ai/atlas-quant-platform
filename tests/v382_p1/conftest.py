"""v3.8.2-P1 兑奖链路状态修复测试配置。"""
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
    """每个测试隔离的 PendingTask 存储目录。"""
    monkeypatch.setenv("ATLAS_TASK_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


@pytest.fixture()
def clean_storage(task_storage):
    """确保测试前后无残留任务。"""
    from engine.task_context import PendingTaskManager
    mgr = PendingTaskManager()
    yield mgr
    mgr.clear_task("default")
