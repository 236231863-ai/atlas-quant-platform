"""v4.5 P1：开奖数据可信中心测试。

覆盖：DataProvider（官方/备用/本地）/ 校验（期号递增/日期/前后区/范围）/ DataHealthReport。
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from engine.data_center import (
    DataHealthBuilder, DataHealthReport, DrawValidator, LocalCache,
    LotteryHealth, OfficialProvider, ValidationResult, build_health_report,
    fetch_with_fallback, get_provider_chain, validate_records,
)
from engine.data_center.providers import BackupProvider, DrawRecord


def rec(num, date="2026-08-01", front=None, back=None, lottery="dlt", pool=0.0):
    return DrawRecord(str(num), date, front or [1, 2, 3, 4, 5],
                      back or [6, 7], lottery, pool)


# ---------- 校验：合法 ----------
def test_validate_valid():
    r = DrawValidator.validate([
        rec(26086), rec(26087, "2026-08-03", [5, 10, 16, 24, 27], [4, 10]),
    ], "dlt", last_issue="26085")
    assert r.valid is True
    assert r.new_issue == "26087"


def test_validate_single():
    r = DrawValidator.validate([rec(26087)], "dlt")
    assert r.valid is True


def test_validate_empty():
    r = DrawValidator.validate([], "dlt")
    assert r.valid is False
    assert "无数据" in r.issues


# ---------- 校验：期号递增 ----------
def test_validate_issue_not_increasing():
    r = DrawValidator.validate([rec(26087)], "dlt", last_issue="26088")
    assert r.valid is False
    assert "未递增" in r.issues[0]


def test_validate_issue_duplicate():
    r = DrawValidator.validate([rec(26087), rec(26087)], "dlt")
    assert r.valid is False


# ---------- 校验：日期 ----------
def test_validate_bad_date():
    r = DrawValidator.validate([rec(26087, "2026/08/03")], "dlt")
    assert r.valid is False
    assert "日期非法" in r.issues[0]


@pytest.mark.parametrize("date", ["2026-08-01", "2025-12-31", "2026-01-01"])
def test_validate_good_dates(date):
    r = DrawValidator.validate([rec(26087, date)], "dlt")
    assert r.valid is True


# ---------- 校验：数量 ----------
@pytest.mark.parametrize("front_n", [3, 4, 6, 7])
def test_validate_front_count(front_n):
    r = DrawValidator.validate([rec(26087, front=[i for i in range(1, front_n + 1)])], "dlt")
    assert r.valid is False
    assert any("前区数量" in i for i in r.issues)


@pytest.mark.parametrize("back_n", [1, 3, 4])
def test_validate_back_count(back_n):
    r = DrawValidator.validate([rec(26087, back=[i for i in range(1, back_n + 1)])], "dlt")
    assert r.valid is False
    assert any("后区数量" in i for i in r.issues)


# ---------- 校验：范围 ----------
@pytest.mark.parametrize("num", [0, 36, 99, -1])
def test_validate_front_range(num):
    r = DrawValidator.validate([rec(26087, front=[1, 2, 3, 4, num])], "dlt")
    assert r.valid is False
    assert any("前区越界" in i for i in r.issues)


@pytest.mark.parametrize("num", [0, 13, 99])
def test_validate_back_range(num):
    r = DrawValidator.validate([rec(26087, back=[1, num])], "dlt")
    assert r.valid is False
    assert any("后区越界" in i for i in r.issues)


# ---------- 校验：双色球 ----------
def test_validate_ssq_valid():
    r = DrawValidator.validate([rec(2026088, "2026-08-02",
                                    [1, 2, 3, 4, 5, 6], [7], "ssq")], "ssq")
    assert r.valid is True


def test_validate_ssq_front_overflow():
    r = DrawValidator.validate([rec(2026088, "2026-08-02",
                                    [1, 2, 3, 4, 5, 34], [7], "ssq")], "ssq")
    assert r.valid is False
    assert any("前区越界" in i for i in r.issues)


def test_validate_ssq_back_overflow():
    r = DrawValidator.validate([rec(2026088, "2026-08-02",
                                    [1, 2, 3, 4, 5, 6], [17], "ssq")], "ssq")
    assert r.valid is False


# ---------- ValidationResult ----------
def test_validation_result_default():
    r = ValidationResult()
    assert r.valid is True
    assert r.issues == []


def test_validation_add_issue():
    r = ValidationResult()
    r.add_issue("x")
    assert r.valid is False
    assert r.issues == ["x"]


# ---------- Providers ----------
def test_official_provider_name():
    assert OfficialProvider("dlt").source_text() == "官方API"


def test_backup_provider_name():
    assert BackupProvider("dlt").source_text() == "内置历史"


def test_provider_chain_length():
    chain = get_provider_chain("dlt")
    assert len(chain) == 3
    assert chain[0].name == "官方API"
    assert chain[2].name == "本地缓存"


def test_local_cache_fetch_sorted(tmp_path):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    # 倒序写入模拟内置
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "5 10 16 24 27|4 10", "pool": "1"},
                   {"issue": "26086", "date": "2026-08-01",
                    "numbers": "10 11 18 22 35|6 12", "pool": "1"}])
    cache = LocalCache("dlt", storage_dir=str(tmp_path))
    recs = cache.fetch_recent(limit=1)
    assert len(recs) == 1
    assert recs[0].number == "26087"  # 最新


def test_local_cache_parse_front_back(tmp_path):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "05 10 16 24 27|04 10", "pool": "1"}])
    cache = LocalCache("dlt", storage_dir=str(tmp_path))
    r = cache.fetch_recent(1)[0]
    assert r.front == [5, 10, 16, 24, 27]
    assert r.back == [4, 10]


# ---------- 数据源链 ----------
def test_fetch_fallback(tmp_path, monkeypatch):
    # 官方失败 → 降级内置
    def boom(*a, **k):
        raise RuntimeError("net down")
    monkeypatch.setattr("engine.data_center_v2.sources.APIDatasource", boom)
    recs, src = fetch_with_fallback("dlt", limit=3, storage_dir=str(tmp_path))
    assert src == "内置历史"
    assert len(recs) > 0


def test_fetch_returns_list(tmp_path):
    recs, src = fetch_with_fallback("dlt", limit=3, storage_dir=str(tmp_path))
    assert isinstance(recs, list)
    assert isinstance(src, str)


# ---------- 健康报告 ----------
def test_health_report_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    rep = build_health_report()
    assert len(rep.items) == 2
    assert rep.items[0].lottery == "dlt"
    assert rep.items[1].lottery == "ssq"


def test_health_report_not_all_trusted(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    rep = build_health_report()
    assert rep.all_trusted is False  # 无 meta → 异常


def test_health_lottery_trusted(tmp_path, monkeypatch):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "5 10 16 24 27|4 10", "pool": "1"}])
    now = datetime(2026, 8, 4, 10, 0)
    up._mark_updated(1, 0)
    import json, os
    with open(up.meta_path, "w", encoding="utf-8") as f:
        json.dump({"updated_at": (now - timedelta(hours=1)).isoformat()}, f)
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = DataHealthBuilder._check_lottery("dlt", now)
    assert h.latest_issue == "26087"
    assert h.status == "可信"
    assert h.valid is True


def test_health_status_stale(tmp_path, monkeypatch):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", str(tmp_path))
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "5 10 16 24 27|4 10", "pool": "1"}])
    now = datetime(2026, 8, 5, 10, 0)
    up._mark_updated(1, 0)
    import json, os
    with open(up.meta_path, "w", encoding="utf-8") as f:
        json.dump({"updated_at": (now - timedelta(hours=30)).isoformat()}, f)
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = DataHealthBuilder._check_lottery("dlt", now)
    assert h.status == "过期"


def test_health_report_summary():
    rep = DataHealthReport(items=[LotteryHealth(lottery="dlt", status="可信")])
    assert "开奖数据健康报告" in rep.summary_text()
    assert "大乐透" in rep.summary_text()


def test_health_to_dict():
    h = LotteryHealth(lottery="dlt", latest_issue="26087", status="可信")
    d = h.to_dict()
    assert d["latest_issue"] == "26087"
    assert d["lottery_name"] == "大乐透"


# ---------- 便捷函数 ----------
def test_validate_records_helper():
    r = validate_records([rec(26087)], "dlt")
    assert r.valid is True
