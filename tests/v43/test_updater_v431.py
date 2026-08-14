"""v4.3.1：开奖数据增量更新器测试。

覆盖：合并去重 / 排序 / 限频 / 写缓存格式 / 静默降级 / 用户缓存优先。
"""
from __future__ import annotations

import json
import os

import pytest

from engine.data_center_v2.updater import (
    IncrementalUpdater, latest_issues, maybe_update_draws,
)


class FakeRecord:
    """模拟 DrawRecord。"""

    def __init__(self, number, date, front, back, pool):
        self.number = number
        self.draw_date = date
        self.front = front
        self.back = back
        self.pool = pool


class FakeAPISource:
    """模拟官方 API（返回固定远程数据）。"""

    def __init__(self, records=None, error=None):
        self._records = records
        self._error = error

    def load(self):
        if self._error:
            raise self._error
        return list(self._records)


def mk_record(num, date="2026-08-03", front=(10, 11, 18, 22, 35), back=(6, 12), pool=8e8):
    return FakeRecord(str(num), date, list(front), list(back), pool)


@pytest.fixture()
def updater(tmp_path):
    return IncrementalUpdater(lottery="dlt", storage_dir=str(tmp_path))


# ---------- merge 去重/排序 ----------
def test_merge_empty(updater):
    assert IncrementalUpdater._merge([], []) == []


def test_merge_no_overlap(updater):
    local = [{"issue": "26085", "date": "2026-07-29", "numbers": "03 04 14 28 31|05 07", "pool": "1"}]
    remote = [{"issue": "26087", "date": "2026-08-03", "numbers": "01 02 03 04 05|06 07", "pool": "2"},
              {"issue": "26086", "date": "2026-08-01", "numbers": "10 11 18 22 35|06 12", "pool": "3"}]
    merged = IncrementalUpdater._merge(local, remote)
    assert [r["issue"] for r in merged] == ["26085", "26086", "26087"]


def test_merge_dedup_keep_newest(updater):
    local = [{"issue": "26086", "date": "2026-08-01", "numbers": "10 11 18 22 35|06 12", "pool": "old"}]
    remote = [{"issue": "26086", "date": "2026-08-01", "numbers": "10 11 18 22 35|06 12", "pool": "new"}]
    merged = IncrementalUpdater._merge(local, remote)
    assert len(merged) == 1
    assert merged[0]["pool"] == "new"  # 远程覆盖


def test_merge_sorted(updater):
    local = [{"issue": "26090", "date": "2026-08-09", "numbers": "1", "pool": "1"},
             {"issue": "26080", "date": "2026-07-25", "numbers": "1", "pool": "1"}]
    remote = [{"issue": "26085", "date": "2026-07-29", "numbers": "1", "pool": "1"}]
    merged = IncrementalUpdater._merge(local, remote)
    assert [r["issue"] for r in merged] == ["26080", "26085", "26090"]


@pytest.mark.parametrize("n_local,n_remote", [(0, 0), (1, 1), (5, 3), (3, 5)])
def test_merge_size_matrix(updater, n_local, n_remote):
    local = [{"issue": str(20000 + i), "date": "", "numbers": "1", "pool": "1"}
             for i in range(n_local)]
    remote = [{"issue": str(30000 + i), "date": "", "numbers": "1", "pool": "1"}
              for i in range(n_remote)]
    merged = IncrementalUpdater._merge(local, remote)
    assert len(merged) == n_local + n_remote


# ---------- 缓存读写格式 ----------
def test_save_load_roundtrip(updater):
    rows = [{"issue": "26086", "date": "2026-08-01", "numbers": "10 11 18 22 35|06 12", "pool": "813207389.58"}]
    updater.save_local(rows)
    loaded = updater.load_local()
    assert loaded == rows


def test_save_creates_file(updater, tmp_path):
    updater.save_local([{"issue": "26086", "date": "", "numbers": "1", "pool": "1"}])
    assert os.path.exists(updater.cache_path())


def test_save_utf8(updater):
    updater.save_local([{"issue": "26086", "date": "", "numbers": "1", "pool": "1"}])
    with open(updater.cache_path(), encoding="utf-8") as f:
        content = f.read()
    assert "issue" in content


def test_load_missing(updater):
    assert updater.load_local() == []


@pytest.mark.parametrize("n", [0, 1, 5, 30])
def test_save_load_matrix(updater, n):
    rows = [{"issue": str(26000 + i), "date": "2026-08-01", "numbers": "1 2 3 4 5|6 7", "pool": "1"}
            for i in range(n)]
    updater.save_local(rows)
    assert len(updater.load_local()) == n


# ---------- 限频 ----------
def test_should_update_initially(updater):
    assert updater.should_update() is True


def test_mark_then_within_age(updater):
    updater._mark_updated(100, 1)
    assert updater.should_update() is False


def test_force_ignores_age(updater, monkeypatch):
    updater._mark_updated(100, 1)
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087)]))
    result = updater.update(force=True)  # force 绕过限频
    assert result["updated"] is True
    assert result["added"] == 1


def test_meta_written(updater, tmp_path):
    updater._mark_updated(120, 3)
    meta = json.load(open(os.path.join(tmp_path, "data_last_update_dlt.json"), encoding="utf-8"))
    assert meta["total"] == 120
    assert meta["added"] == 3
    assert meta["lottery"] == "dlt"


# ---------- update 全流程（mock API） ----------
def test_update_adds_new(updater, monkeypatch):
    updater.save_local([{"issue": "26086", "date": "2026-08-01",
                         "numbers": "10 11 18 22 35|06 12", "pool": "1"}])
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087), mk_record(26086)]))
    result = updater.update(force=True)
    assert result["updated"] is True
    assert result["added"] == 1
    assert result["total"] == 2
    assert result["error"] is None
    issues = [r["issue"] for r in updater.load_local()]
    assert "26087" in issues


def test_update_within_age_skips(updater, monkeypatch):
    updater._mark_updated(100, 0)
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087)]))
    result = updater.update()  # 不限频，应跳过
    assert result["updated"] is False
    assert result["reason"] == "within_age"


def test_update_api_empty(updater, monkeypatch):
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([]))
    result = updater.update(force=True)
    assert result["updated"] is False
    assert result["reason"] == "no_remote_data"


def test_update_exception_silent(updater, monkeypatch):
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource(error=RuntimeError("net down")))
    result = updater.update(force=True)
    assert result["updated"] is False
    assert result["error"]  # 记录错误但不上抛
    assert result["reason"] == "exception"


def test_update_writes_meta(updater, monkeypatch):
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087)]))
    updater.update(force=True)
    assert updater.should_update() is False  # 已标记


def test_update_no_dedup(updater, monkeypatch):
    updater.save_local([{"issue": "26087", "date": "2026-08-03",
                         "numbers": "01 02 03 04 05|06 07", "pool": "1"}])
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087)]))
    result = updater.update(force=True)
    assert result["added"] == 0  # 已存在，不重复
    assert result["total"] == 1


@pytest.mark.parametrize("n_remote", [0, 1, 5, 30])
def test_update_matrix(updater, monkeypatch, n_remote):
    """首次更新以内置历史为 base（不丢历史），新增 = 远程期数。"""
    records = [mk_record(27000 + i) for i in range(n_remote)]
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource(records))
    result = updater.update(force=True)
    if n_remote == 0:
        assert result["updated"] is False
    else:
        assert result["updated"] is True
        assert result["added"] == n_remote
        assert result["total"] >= n_remote  # 内置 base + 新增


# ---------- 便捷函数 ----------
def test_maybe_update_helper(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    monkeypatch.setattr("engine.data_center_v2.updater.APIDatasource",
                        lambda **kw: FakeAPISource([mk_record(26087)]))
    result = maybe_update_draws("dlt", force=True)
    assert isinstance(result, dict)
    assert result["updated"] is True


def test_latest_issues(tmp_path):
    upd = IncrementalUpdater(lottery="dlt", storage_dir=str(tmp_path))
    upd.save_local([{"issue": "26085", "date": "", "numbers": "1", "pool": "1"},
                    {"issue": "26086", "date": "", "numbers": "1", "pool": "1"},
                    {"issue": "26087", "date": "", "numbers": "1", "pool": "1"}])
    issues = [r["issue"] for r in upd.load_local()]
    assert issues == ["26085", "26086", "26087"]


# ---------- 多彩种 / 优雅降级（v4.3.1 修复） ----------
def test_api_game_no_switch():
    """APIDatasource 按彩种切换 gameNo（dlt=85；ssq 走福彩 CWLDatasource，v4.10.1 修复）。"""
    from engine.data_center_v2.sources import APIDatasource, CWLDatasource
    assert APIDatasource("dlt")._game_no == "85"
    assert APIDatasource("unknown")._game_no == "85"  # 默认回退
    # 双色球属福彩，不再用体彩 APIDatasource 的 gameNo
    assert CWLDatasource("ssq").lottery == "ssq"


def test_update_ssq_api_empty_preserves(tmp_path, monkeypatch):
    """ssq API 为空时不得覆盖已有缓存（优雅降级）。"""
    upd = IncrementalUpdater(lottery="ssq", storage_dir=str(tmp_path))
    upd.save_local([{"issue": "2026087", "date": "2026-07-30",
                     "numbers": "04 06 10 18 23 31|11", "pool": "1"}])
    monkeypatch.setattr("engine.data_center_v2.updater.CWLDatasource",
                        lambda **kw: FakeAPISource([]))
    result = upd.update(force=True)
    assert result["updated"] is False
    assert result["reason"] == "no_remote_data"
    # 本地缓存未被破坏
    rows = upd.load_local()
    assert len(rows) == 1
    assert rows[0]["issue"] == "2026087"
    assert "04 06 10 18 23 31|11" in rows[0]["numbers"]
