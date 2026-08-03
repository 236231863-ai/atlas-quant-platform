"""v4.4 P3：Data Health Center 测试。

覆盖：等级判定（A/B/C/D）/ 年龄计算 / check 各彩种 / 便捷函数。
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from engine.live_draw.health import (
    LEVELS, DataHealth, DataHealthCenter, check_data_health,
)


# ---------- 等级判定 ----------
@pytest.mark.parametrize("age,expect", [
    (0, "A"), (5, "A"), (11.9, "A"),
    (12, "B"), (18, "B"), (23.9, "B"),
    (24, "C"), (48, "C"), (100, "C"),
    (-1, "D"),
])
def test_level_of_matrix(age, expect):
    assert DataHealthCenter.level_of(age, has_data=True) == expect


def test_level_no_data():
    assert DataHealthCenter.level_of(0, has_data=False) == "D"


def test_level_negative_age():
    assert DataHealthCenter.level_of(-1) == "D"


# ---------- 年龄计算 ----------
def test_age_hours_empty():
    assert DataHealthCenter._age_hours(None) == -1.0


def test_age_hours_recent():
    now = datetime(2026, 8, 4, 10, 0)
    dt = (now - timedelta(hours=3)).isoformat()
    assert abs(DataHealthCenter._age_hours(dt, now) - 3.0) < 0.01


def test_age_hours_invalid():
    assert DataHealthCenter._age_hours("not-a-date") == -1.0


def test_age_hours_zero():
    now = datetime(2026, 8, 4, 10, 0)
    assert DataHealthCenter._age_hours(now.isoformat(), now) == 0.0


# ---------- DataHealth 结构 ----------
def test_health_default():
    h = DataHealth()
    assert h.level == "D"
    assert h.lottery_name == "大乐透"


def test_health_ssq_name():
    assert DataHealth(lottery="ssq").lottery_name == "双色球"


def test_health_age_text_unknown():
    h = DataHealth(age_hours=-1)
    assert h.age_text == "未知"


def test_health_age_text_minutes():
    h = DataHealth(age_hours=0.5)
    assert "分钟前" in h.age_text


def test_health_age_text_hours():
    h = DataHealth(age_hours=3.0)
    assert "3.0 小时前" in h.age_text


def test_health_to_dict():
    h = DataHealth(lottery="dlt", latest_issue="26087", level="A")
    d = h.to_dict()
    assert d["level"] == "A"
    assert d["lottery_name"] == "大乐透"


def test_health_summary_text():
    h = DataHealth(lottery="dlt", latest_issue="26087", draw_date="2026-08-03",
                   age_hours=5.0, level="A", source="实时更新", message="正常同步")
    text = h.summary_text()
    assert "A 级" in text
    assert "26087" in text
    assert "5.0" in text


# ---------- check 彩种 ----------
def test_check_dlt(tmp_path, monkeypatch):
    from engine.data_center_v2.updater import IncrementalUpdater
    up = IncrementalUpdater("dlt", storage_dir=str(tmp_path))
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "05 10 16 24 27|04 10", "pool": "1"}])
    up._mark_updated(1, 1)
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = DataHealthCenter.check("dlt")
    assert h.latest_issue == "26087"
    assert h.total == 1
    assert h.level in LEVELS


def test_check_no_data(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = DataHealthCenter.check("dlt")
    assert h.level == "D"
    assert h.message == "数据异常"


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_check_all(tmp_path, monkeypatch, lottery):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    healths = DataHealthCenter.check_all()
    assert len(healths) == 2
    assert all(h.level in LEVELS for h in healths)


def test_check_all_with_data(tmp_path, monkeypatch):
    from engine.data_center_v2.updater import IncrementalUpdater
    for lot in ("dlt", "ssq"):
        up = IncrementalUpdater(lot, storage_dir=str(tmp_path))
        up.save_local([{"issue": "26087" if lot == "dlt" else "2026087",
                        "date": "2026-08-03", "numbers": "1 2 3 4 5|6 7", "pool": "1"}])
        up._mark_updated(1, 0)
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    healths = DataHealthCenter.check_all()
    assert len(healths) == 2
    assert healths[0].lottery == "dlt"


# ---------- 便捷函数 ----------
def test_check_helper(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    h = check_data_health("dlt")
    assert isinstance(h, DataHealth)


# ---------- 等级阈值矩阵 ----------
@pytest.mark.parametrize("hours", [i * 2 for i in range(15)])
def test_level_hours_scale(hours):
    """0-28h 等级单调性：0<12→A, 12≤x<24→B, ≥24→C。"""
    level = DataHealthCenter.level_of(hours)
    if hours < 12:
        assert level == "A"
    elif hours < 24:
        assert level == "B"
    else:
        assert level == "C"
