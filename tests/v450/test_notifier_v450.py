"""v4.5 P3：Windows 后台提醒测试。

覆盖：通知通道（toast/msg/log）/ 降级链 / 开奖/中奖/待兑奖提醒 / 日志兜底。
"""
from __future__ import annotations

import json
import os

import pytest

from engine.draw_monitor import WindowsNotifier, notify_draw_event
from engine.live_draw import DrawEvent


@pytest.fixture()
def notifier(tmp_path):
    return WindowsNotifier(storage_dir=str(tmp_path))


class FakeProc:
    def __init__(self, returncode=0, stdout="OK"):
        self.returncode = returncode
        self.stdout = stdout


# ---------- 通知日志兜底 ----------
def test_notify_log_writes(notifier, tmp_path):
    ok = notifier.notify_log("reminder", "标题", "内容")
    assert ok is True
    path = os.path.join(str(tmp_path), "notifications.jsonl")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        line = json.loads(f.readline())
    assert line["kind"] == "reminder"
    assert line["title"] == "标题"


def test_notify_log_appends(notifier, tmp_path):
    notifier.notify_log("a", "t1", "m1")
    notifier.notify_log("b", "t2", "m2")
    with open(os.path.join(str(tmp_path), "notifications.jsonl"), encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2


# ---------- notify 统一入口 ----------
def test_notify_falls_back_to_log(notifier, monkeypatch, tmp_path):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: False)
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_msg",
                        lambda self, t, m: False)
    r = notifier.notify("标题", "内容", kind="reminder")
    assert r["log"] is True
    assert r["toast"] is False
    assert r["msg"] is False
    # 日志兜底已写
    assert os.path.exists(os.path.join(str(tmp_path), "notifications.jsonl"))


def test_notify_toast_success(notifier, monkeypatch):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: True)
    r = notifier.notify("标题", "内容")
    assert r["toast"] is True


def test_notify_msg_fallback(notifier, monkeypatch):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: False)
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_msg",
                        lambda self, t, m: True)
    r = notifier.notify("标题", "内容")
    assert r["msg"] is True


# ---------- 便捷提醒 ----------
def test_draw_reminder(notifier, monkeypatch, tmp_path):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: False)
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_msg",
                        lambda self, t, m: False)
    r = notifier.notify_draw_reminder("大乐透", "26087", pending=2)
    assert r["log"] is True
    path = os.path.join(str(tmp_path), "notifications.jsonl")
    with open(path, encoding="utf-8") as f:
        d = json.loads(f.readline())
    assert d["kind"] == "draw_reminder_received"
    assert "大乐透" in d["title"]


def test_win_reminder(notifier, monkeypatch, tmp_path):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: False)
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_msg",
                        lambda self, t, m: False)
    r = notifier.notify_win("大乐透", 1, 5000000, "26087")
    assert r["log"] is True
    with open(os.path.join(str(tmp_path), "notifications.jsonl"), encoding="utf-8") as f:
        d = json.loads(f.readline())
    assert d["kind"] == "win"
    assert "中奖" in d["title"]


def test_pending_reminder(notifier, monkeypatch, tmp_path):
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_toast",
                        lambda self, t, m: False)
    monkeypatch.setattr("engine.draw_monitor.notifier.WindowsNotifier.notify_msg",
                        lambda self, t, m: False)
    r = notifier.notify_pending("大乐透", 3)
    assert r["log"] is True
    with open(os.path.join(str(tmp_path), "notifications.jsonl"), encoding="utf-8") as f:
        d = json.loads(f.readline())
    assert d["kind"] == "pending_claim"
    assert "3 张" in d["message"]


# ---------- draw_updated 事件 → 通知 ----------
def test_notify_draw_event(monkeypatch, tmp_path):
    from engine.draw_monitor import notifier as mod
    monkeypatch.setattr(mod.WindowsNotifier, "notify_toast", lambda self, t, m: False)
    monkeypatch.setattr(mod.WindowsNotifier, "notify_msg", lambda self, t, m: False)
    monkeypatch.setattr(mod.WindowsNotifier, "notify_log", lambda self, k, t, m: True)
    ev = DrawEvent(event_type="draw_updated", lottery="dlt",
                   issue="26087", draw_date="2026-08-03")
    r = notify_draw_event(ev)
    assert isinstance(r, dict)


# ---------- Toast 命令构造（不实际执行） ----------
def test_notify_toast_command(notifier, monkeypatch):
    """验证 PowerShell 命令含标题与消息。"""
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return FakeProc(0, "OK")

    monkeypatch.setattr("engine.draw_monitor.notifier.subprocess.run", fake_run)
    ok = notifier.notify_toast("测试标题", "测试消息")
    assert ok is True
    joined = " ".join(captured["cmd"])
    assert "ToastNotificationManager" in joined
    assert "测试标题" in joined
    assert "测试消息" in joined


def test_notify_msg_command(notifier, monkeypatch):
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return FakeProc(0)

    monkeypatch.setattr("engine.draw_monitor.notifier.subprocess.run", fake_run)
    ok = notifier.notify_msg("标题", "消息")
    assert ok is True
    assert captured["cmd"][0].lower() == "msg"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("kind", ["draw_reminder_received", "win", "pending_claim", "reminder"])
def test_notify_kinds(kind, notifier, tmp_path):
    ok = notifier.notify_log(kind, "t", "m")
    assert ok is True
    with open(os.path.join(str(tmp_path), "notifications.jsonl"), encoding="utf-8") as f:
        assert json.loads(f.readline())["kind"] == kind
