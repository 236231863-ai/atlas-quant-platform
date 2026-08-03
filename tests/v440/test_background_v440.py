"""v4.4 P2：Atlas Background Service 测试。

覆盖：安装/卸载/状态查询（mock schtasks）+ worker 同步入口。
"""
from __future__ import annotations

import subprocess

import pytest

from engine.live_draw.background import (
    TASK_NAME, TASK_PATH, BackgroundServiceManager, service_cli,
)


class FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture()
def fake_schtasks(monkeypatch):
    """mock subprocess.run，记录命令并返回预设结果。"""
    calls = []

    def _has(cmd, frag):
        return any(frag in str(arg) for arg in cmd)

    def _run(cmd, **kw):
        calls.append(cmd)
        if _has(cmd, "/Delete"):
            return FakeProc(0, "删除任务成功")
        if _has(cmd, "/Query"):
            name = cmd[cmd.index("/TN") + 1] if "/TN" in cmd else ""
            if name == TASK_PATH and "Boot" not in name:
                return FakeProc(0, "任务状态: Running")
            if "Boot" in name:
                return FakeProc(0, "任务已就绪")
            return FakeProc(1, "错误: 系统找不到指定的任务")
        if _has(cmd, "/Create"):
            return FakeProc(0, "成功: 计划任务已创建")
        return FakeProc(0, "ok")

    monkeypatch.setattr("engine.live_draw.background._run", _run)
    return calls


# ---------- 安装 ----------
def test_install_ok(fake_schtasks):
    r = BackgroundServiceManager.install(interval_minutes=30)
    assert r["ok"] is True
    assert r["task"] == TASK_PATH


def _has_frag(cmd, frag):
    return any(frag in str(arg) for arg in cmd)


def test_install_calls_schtasks_create(fake_schtasks):
    BackgroundServiceManager.install()
    create_calls = [c for c in fake_schtasks if _has_frag(c, "/Create")]
    assert len(create_calls) >= 1
    # 包含 MINUTE 触发
    assert any(_has_frag(c, "MINUTE") for c in create_calls)


def test_install_creates_boot(fake_schtasks):
    BackgroundServiceManager.install(on_startup=True)
    boot_calls = [c for c in fake_schtasks if _has_frag(c, "ONSTART")]
    assert len(boot_calls) == 1


def test_install_skip_boot(fake_schtasks):
    BackgroundServiceManager.install(on_startup=False)
    boot_calls = [c for c in fake_schtasks if _has_frag(c, "ONSTART")]
    assert len(boot_calls) == 0


def test_install_missing_worker(fake_schtasks, monkeypatch):
    monkeypatch.setattr("engine.live_draw.background._worker_script",
                        lambda: "C:/nonexistent/worker.py")
    r = BackgroundServiceManager.install()
    assert r["ok"] is False
    assert "不存在" in r["detail"]


# ---------- 卸载 ----------
def test_uninstall_ok(fake_schtasks):
    r = BackgroundServiceManager.uninstall()
    assert r["ok"] is True


def test_uninstall_calls_delete(fake_schtasks):
    BackgroundServiceManager.uninstall()
    delete_calls = [c for c in fake_schtasks if _has_frag(c, "/Delete")]
    assert len(delete_calls) == 2  # 主任务 + 开机任务


# ---------- 状态查询 ----------
def test_status_installed(fake_schtasks):
    s = BackgroundServiceManager.status()
    assert s["installed"] is True
    assert s["state"] == "running"  # mock 返回 Running


def test_status_not_installed(monkeypatch):
    monkeypatch.setattr("engine.live_draw.background._run",
                        lambda cmd, **kw: FakeProc(1, "错误: 找不到"))
    s = BackgroundServiceManager.status()
    assert s["installed"] is False
    assert s["state"] == "not_installed"


def test_status_boot_flag(fake_schtasks):
    s = BackgroundServiceManager.status()
    assert s["boot_on_startup"] is True


# ---------- CLI ----------
def test_cli_install(fake_schtasks):
    r = service_cli("install")
    assert r["ok"] is True


def test_cli_uninstall(fake_schtasks):
    r = service_cli("uninstall")
    assert r["ok"] is True


def test_cli_status(fake_schtasks):
    r = service_cli("status")
    assert r["task"] == TASK_PATH


def test_cli_unknown():
    r = service_cli("hack")
    assert r["ok"] is False


# ---------- 常量 ----------
def test_task_name():
    assert TASK_NAME == "AtlasLiveDrawSync"
    assert TASK_PATH == "Atlas\\AtlasLiveDrawSync"
