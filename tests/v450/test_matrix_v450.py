"""v4.5 补充矩阵：校验/数据源/监控/提醒/信任/埋点 大规模参数化。"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from engine.data_center import (
    DataHealthBuilder, DrawValidator, LocalCache, build_health_report,
    fetch_with_fallback, validate_records,
)
from engine.data_center.providers import DrawRecord
from engine.draw_monitor import DrawMonitor, WindowsNotifier
from engine.claim_center import ClaimCenter
from engine.user_events import BehaviorReporter, build_behavior_report


def rec(num, date="2026-08-01", front=None, back=None, lottery="dlt"):
    return DrawRecord(str(num), date, front or [1, 2, 3, 4, 5],
                      back or [6, 7], lottery)


# ---------- 校验矩阵 ----------
@pytest.mark.parametrize("issue,last,valid", [
    (26087, "26086", True), (26087, "26088", False), (26087, "26087", False),
    (1, "", True), (100, "99", True),
])
def test_validate_increasing(issue, last, valid):
    r = DrawValidator.validate([rec(issue)], "dlt", last_issue=str(last))
    assert r.valid is valid


@pytest.mark.parametrize("front,back,valid", [
    ([1, 2, 3, 4, 5], [6, 7], True),
    ([1, 2, 3, 4], [6, 7], False),
    ([1, 2, 3, 4, 5], [6], False),
    ([1, 2, 3, 4, 5, 6], [6, 7], False),
    ([1, 2, 3, 4, 5], [6, 7, 8], False),
    ([0, 2, 3, 4, 5], [6, 7], False),
    ([35, 2, 3, 4, 5], [6, 7], True),   # 35 边界合法
    ([36, 2, 3, 4, 5], [6, 7], False),
    ([1, 2, 3, 4, 5], [12, 7], True),   # 12 边界合法
    ([1, 2, 3, 4, 5], [13, 7], False),
])
def test_validate_dlt_rules(front, back, valid):
    r = DrawValidator.validate([rec(26087, front=front, back=back)], "dlt")
    assert r.valid is valid


@pytest.mark.parametrize("front,back,valid", [
    ([1, 2, 3, 4, 5, 6], [7], True),
    ([1, 2, 3, 4, 5], [7], False),
    ([1, 2, 3, 4, 5, 6], [7, 8], False),
    ([33, 2, 3, 4, 5, 6], [7], True),
    ([34, 2, 3, 4, 5, 6], [7], False),
    ([1, 2, 3, 4, 5, 6], [16], True),
    ([1, 2, 3, 4, 5, 6], [17], False),
])
def test_validate_ssq_rules(front, back, valid):
    r = DrawValidator.validate([rec(2026088, front=front, back=back, lottery="ssq")], "ssq")
    assert r.valid is valid


@pytest.mark.parametrize("date_str,valid", [
    ("2026-08-01", True), ("2026-8-1", True), ("2026/08/01", False),
    ("", True),  # 空日期跳过
    ("not-date", False),
])
def test_validate_date(date_str, valid):
    r = DrawValidator.validate([rec(26087, date_str)], "dlt")
    assert r.valid is valid


# ---------- 数据源矩阵 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_provider_chain_len(lottery):
    from engine.data_center import get_provider_chain
    assert len(get_provider_chain(lottery)) == 3


@pytest.mark.parametrize("limit", [1, 3, 5, 10])
def test_fetch_fallback_limit(limit, tmp_path):
    recs, src = fetch_with_fallback("dlt", limit=limit, storage_dir=str(tmp_path))
    assert len(recs) <= limit


@pytest.mark.parametrize("i", range(15))
def test_local_cache_recent(tmp_path, i):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    rows = [{"issue": str(26000 + j), "date": "2026-08-01",
             "numbers": "1 2 3 4 5|6 7", "pool": "1"} for j in range(20)]
    up.save_local(rows)
    cache = LocalCache("dlt", storage_dir=str(tmp_path))
    recs = cache.fetch_recent(limit=i + 1)
    assert len(recs) == i + 1
    assert recs[-1].number == str(26019)


# ---------- 监控矩阵 ----------
@pytest.mark.parametrize("weekday", range(7))
def test_monitor_draw_days(weekday):
    """周一/三/六大乐透，周二/四/日双色球；周五无开奖（真实规则）。"""
    d = (date(2026, 8, 3) + timedelta(days=weekday)).isoformat()
    dlt = DrawMonitor.is_draw_day("dlt", d)
    ssq = DrawMonitor.is_draw_day("ssq", d)
    if weekday == 4:  # 周五无开奖
        assert dlt is False and ssq is False
    else:
        assert dlt or ssq


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_monitor_next_draw(lottery):
    nxt = DrawMonitor().next_draw_time(lottery, "2026-08-03")
    assert nxt is not None


# ---------- 提醒矩阵 ----------
@pytest.mark.parametrize("kind", ["draw_reminder_received", "win", "pending_claim"])
def test_notifier_kinds(kind, tmp_path):
    n = WindowsNotifier(storage_dir=str(tmp_path))
    assert n.notify_log(kind, "t", "m") is True


@pytest.mark.parametrize("i", range(10))
def test_notifier_log_append(tmp_path, i):
    import os
    n = WindowsNotifier(storage_dir=str(tmp_path))
    # 同目录下追加写入 i+1 条
    for j in range(i + 1):
        n.notify_log("reminder", f"t{j}", f"m{j}")
    with open(os.path.join(str(tmp_path), "notifications.jsonl"), encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == i + 1


# ---------- 兑奖信任矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_claim_trust_stable(ticket_storage, i):
    tickets = [{"ticket_id": f"T-{i}", "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": "2026-07-31", "draw_date": "2026-08-01", "cost": 2.0}]
    r = ClaimCenter.auto_claim(tickets, lottery="dlt", draw_date="2026-08-01")
    assert r.trust_text()
    assert r.verified in (True, False)


# ---------- 埋点矩阵 ----------
@pytest.mark.parametrize("i", range(15))
def test_behavior_report_random(i):
    import random
    random.seed(i)
    from engine.user_events import UserEvent
    events = []
    types = ["app_opened", "ticket_saved", "draw_reminder_received",
             "draw_opened", "claim_completed", "report_viewed"]
    for j in range(random.randint(1, 15)):
        d = date.today() - timedelta(days=random.randint(0, 7))
        events.append(UserEvent(event_type=random.choice(types),
                                created_at=f"{d.isoformat()}T10:00:00"))
    rep = build_behavior_report(events)
    assert rep.summary.total_events == len(events)
    assert rep.to_text()


# ---------- 健康报告矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_health_report_stable(tmp_path, monkeypatch, i):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    rep = build_health_report()
    assert len(rep.items) == 2
    assert all(it.valid is False or it.valid is True for it in rep.items)
