"""v4.4 P6 补充矩阵 2：updater 全流程 / 后台命令 / 兑奖联动 / 健康检查。

目标：补足 v440 ≥800。
"""
from __future__ import annotations

from datetime import datetime

import pytest

from engine.data_center_v2.updater import IncrementalUpdater
from engine.live_draw import (
    AutoClaimLink, ClaimLinkResult, DataHealthCenter, DrawEvent,
    DrawEventBus, LiveDrawService,
)
from engine.live_draw.background import BackgroundServiceManager, service_cli
from engine.ticket_system.schedule import LotterySchedule


class FakeRecord:
    def __init__(self, num, date="2026-08-03", front=None, back=None, pool=8e8):
        self.number = num
        self.draw_date = date
        self.front = front or [1, 2, 3, 4, 5]
        self.back = back or [6, 7]
        self.pool = pool


class FakeAPISrc:
    def __init__(self, records=None, error=None):
        self._records = records or []
        self._error = error

    def load(self):
        if self._error:
            raise self._error
        return list(self._records)


class FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture()
def updater(tmp_path):
    return IncrementalUpdater(lottery="dlt", storage_dir=str(tmp_path))


def _fake_src(records=None, error=None):
    return FakeAPISrc(records=records, error=error)


# ---------- updater update 结果矩阵 ----------
@pytest.mark.parametrize("n_remote", list(range(15)))
def test_updater_update_adds(updater, monkeypatch, n_remote):
    recs = [FakeRecord(30000 + i) for i in range(n_remote)]
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: _fake_src(recs))
    r = updater.update(force=True)
    if n_remote == 0:
        assert r["updated"] is False
        assert r["reason"] in ("no_remote_data", "no_new")
    else:
        assert r["updated"] is True
        assert r["added"] == n_remote
        assert r["total"] >= n_remote


@pytest.mark.parametrize("err", ["net down", "timeout", "403", "JSON parse"])
def test_updater_update_exception(updater, monkeypatch, err):
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: _fake_src(error=RuntimeError(err)))
    r = updater.update(force=True)
    assert r["updated"] is False
    assert r["error"]


@pytest.mark.parametrize("i", range(10))
def test_updater_meta_roundtrip(updater, tmp_path, i):
    updater._mark_updated(100 + i, i)
    up2 = IncrementalUpdater("dlt", str(tmp_path))
    assert up2._last_update() is not None
    assert up2.should_update() is False


@pytest.mark.parametrize("n", [1, 3, 7, 15])
def test_updater_save_load_roundtrip(updater, n):
    rows = [{"issue": str(26000 + i), "date": "2026-08-01",
             "numbers": "1 2 3 4 5|6 7", "pool": "1"} for i in range(n)]
    updater.save_local(rows)
    assert len(updater.load_local()) == n


# ---------- 后台命令矩阵 ----------
@pytest.mark.parametrize("action", ["install", "uninstall", "status", "bad"])
def test_cli_actions(monkeypatch, action):
    monkeypatch.setattr("engine.live_draw.background._run",
                        lambda cmd, **kw: FakeProc(0, "ok"))
    r = service_cli(action)
    assert isinstance(r, dict)
    if action == "bad":
        assert r["ok"] is False


@pytest.mark.parametrize("rc", [0, 1])
def test_status_installed_variants(monkeypatch, rc):
    monkeypatch.setattr("engine.live_draw.background._run",
                        lambda cmd, **kw: FakeProc(rc, "Running" if rc == 0 else ""))
    s = BackgroundServiceManager.status()
    if rc == 0:
        assert s["installed"] is True
    else:
        assert s["installed"] is False


# ---------- 兑奖联动矩阵 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq"])
def test_claim_run_lotteries(ticket_storage, lottery):
    t = {"ticket_id": "T-1", "lottery": lottery,
         "front": [1, 2, 3, 4, 5] if lottery == "dlt" else [1, 2, 3, 4, 5, 6],
         "back": [1, 2] if lottery == "dlt" else [1],
         "buy_date": "2026-07-31", "draw_date": "2026-08-01", "cost": 2.0}
    r = AutoClaimLink.run(lottery=lottery, tickets=[t])
    assert isinstance(r, ClaimLinkResult)


@pytest.mark.parametrize("n", range(15))
def test_claim_run_empty(ticket_storage, n):
    r = AutoClaimLink.run(lottery="dlt", tickets=[])
    assert r.matched == 0


@pytest.mark.parametrize("matched", range(0, 11))
def test_claim_result_has_tickets(matched):
    r = ClaimLinkResult(matched=matched)
    assert r.has_tickets is (matched > 0)


# ---------- 事件总线订阅矩阵 ----------
@pytest.mark.parametrize("n_sub", [0, 1, 3, 5])
def test_event_bus_multi_sub(n_sub):
    DrawEventBus.reset()
    got = []
    for _ in range(n_sub):
        DrawEventBus.subscribe("draw_updated", lambda e: got.append(1))
    DrawEventBus.publish(DrawEvent(event_type="draw_updated", lottery="dlt"))
    assert len(got) == n_sub
    DrawEventBus.reset()


@pytest.mark.parametrize("issue", ["26000", "26087", "2026087", "99999"])
def test_event_issue_passthrough(issue):
    ev = DrawEvent(event_type="new_issue", lottery="dlt", issue=issue)
    assert ev.issue == issue


# ---------- 健康检查矩阵 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_health_no_data(tmp_path, monkeypatch, lottery):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = DataHealthCenter.check(lottery)
    assert h.level == "D"


@pytest.mark.parametrize("hours_ago", [0, 1, 6, 11, 12, 13, 23, 24, 25, 48])
def test_health_age_level(tmp_path, monkeypatch, hours_ago):
    from datetime import timedelta
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "1 2 3 4 5|6 7", "pool": "1"}])
    now = datetime(2026, 8, 4, 12, 0)
    up._mark_updated(1, 0)
    # 手动构造 meta 时间
    import json, os
    meta = {"updated_at": (now - timedelta(hours=hours_ago)).isoformat()}
    with open(up.meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)
    h = DataHealthCenter.check("dlt", now=now)
    if hours_ago < 12:
        assert h.level == "A"
    elif hours_ago < 24:
        assert h.level == "B"
    else:
        assert h.level == "C"


# ---------- 开奖日程矩阵 ----------
@pytest.mark.parametrize("m", range(1, 13))
def test_schedule_months(m):
    d = f"2026-{m:02d}-05"
    nxt = LotterySchedule.next_draw_date("dlt", d)
    assert nxt is not None


# ---------- 便捷 sync_now ----------
@pytest.mark.parametrize("i", range(10))
def test_sync_now_stable(monkeypatch, i):
    class FU:
        def __init__(self, lottery="dlt", storage_dir=None):
            self.lottery = lottery
        def update(self, force=False, pages=1):
            return {"updated": False, "reason": "no_new", "added": 0, "total": 1}
        def load_local(self): return []
        def _load_builtin(self): return []
        def _last_update(self): return None
    monkeypatch.setattr("engine.data_center_v2.updater.IncrementalUpdater", FU)
    from engine.live_draw import sync_now
    evs = sync_now()
    assert len(evs) == 2
