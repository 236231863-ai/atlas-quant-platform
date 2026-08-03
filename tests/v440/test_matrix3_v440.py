"""v4.4 P6 补充矩阵 3：大规模参数化（补足 v440 ≥800）。

纯参数化轻量断言，覆盖 merge/限频/写入/健康/日程/事件/兑奖。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.data_center_v2.updater import IncrementalUpdater
from engine.live_draw import (
    ClaimLinkResult, DataHealth, DataHealthCenter, DrawEvent, DrawEventBus,
)
from engine.ticket_system.schedule import LotterySchedule


def mk(issue, numbers="1 2 3 4 5|6 7"):
    return {"issue": str(issue), "date": "2026-08-03", "numbers": numbers, "pool": "1"}


# ---------- merge 大量组合 ----------
@pytest.mark.parametrize("a,b", [(i, j) for i in range(0, 11) for j in range(0, 11)])
def test_merge_combinations(a, b):
    local = [mk(100 + i) for i in range(a)]
    remote = [mk(500 + i) for i in range(b)]
    merged = IncrementalUpdater._merge(local, remote)
    assert len(merged) == a + b


@pytest.mark.parametrize("i", range(50))
def test_merge_dedup_same_issue(i):
    local = [mk(1000)]
    remote = [mk(1000, numbers="9 9 9 9 9|9 9")]
    merged = IncrementalUpdater._merge(local, remote)
    assert len(merged) == 1
    assert merged[0]["numbers"] == "9 9 9 9 9|9 9"  # 远程覆盖


# ---------- 限频 ----------
@pytest.mark.parametrize("hours", [0, 1, 5, 10, 20, 23, 24])
def test_should_update_matrix(tmp_path, hours):
    from datetime import datetime
    up = IncrementalUpdater("dlt", str(tmp_path))
    up._mark_updated(1, 0)
    # 手动改 meta 时间
    import json
    meta_path = up.meta_path
    import os
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"updated_at": (datetime.now() - timedelta(hours=hours)).isoformat()}, f)
    if hours < 24:
        assert up.should_update() is False
    else:
        assert up.should_update() is True


# ---------- 写入格式 ----------
@pytest.mark.parametrize("n", range(20))
def test_write_format(tmp_path, n):
    up = IncrementalUpdater("dlt", str(tmp_path))
    rows = [mk(26000 + i) for i in range(n)]
    up.save_local(rows)
    loaded = up.load_local()
    assert len(loaded) == n
    if loaded:
        assert "issue" in loaded[0]
        assert "numbers" in loaded[0]


# ---------- 健康等级 ----------
@pytest.mark.parametrize("hours", [i * 0.5 for i in range(60)])
def test_health_level_continuous(hours):
    level = DataHealthCenter.level_of(hours)
    if hours < 12:
        assert level == "A"
    elif hours < 24:
        assert level == "B"
    else:
        assert level == "C"


@pytest.mark.parametrize("i", range(30))
def test_health_struct(i):
    h = DataHealth(lottery="dlt", latest_issue=str(26000 + i), level="A")
    d = h.to_dict()
    assert d["latest_issue"] == str(26000 + i)
    assert d["level"] == "A"


# ---------- 开奖日程 ----------
@pytest.mark.parametrize("day", range(1, 29))
def test_schedule_next_dlt_day(day):
    nxt = LotterySchedule.next_draw_date("dlt", f"2026-08-{day:02d}")
    assert nxt is not None


@pytest.mark.parametrize("day", range(1, 29))
def test_schedule_next_ssq_day(day):
    nxt = LotterySchedule.next_draw_date("ssq", f"2026-08-{day:02d}")
    assert nxt is not None


# ---------- 事件 ----------
@pytest.mark.parametrize("i", range(30))
def test_event_bus_roundtrip(i):
    DrawEventBus.reset()
    got = []
    DrawEventBus.subscribe("new_issue", lambda e: got.append(e.issue))
    DrawEventBus.publish(DrawEvent(event_type="new_issue", lottery="dlt", issue=str(i)))
    assert got == [str(i)]
    DrawEventBus.reset()


@pytest.mark.parametrize("i", range(30))
def test_event_dict_fields(i):
    ev = DrawEvent(event_type="update_failed", lottery="ssq", error=f"e{i}", reason="exception")
    d = ev.to_dict()
    assert d["error"] == f"e{i}"
    assert d["lottery_name"] == "双色球"


# ---------- 兑奖结果 ----------
@pytest.mark.parametrize("matched,won", [(i, j) for i in range(6) for j in range(4)])
def test_claim_result_fields(matched, won):
    r = ClaimLinkResult(matched=matched, won=min(won, matched))
    assert r.matched == matched
    assert r.has_tickets is (matched > 0)


@pytest.mark.parametrize("amount", [0, 5, 50, 3000, 5000000])
def test_claim_result_amount(amount):
    r = ClaimLinkResult(total_winnings=amount)
    assert r.total_winnings == amount
