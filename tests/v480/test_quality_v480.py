"""v4.8 P5：数据质量系统测试。

覆盖：重复票/错误号码/日期异常/金额异常/彩种错误 → 可信等级 A/B/C。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.data_quality import DataQualityChecker, QualityReport, check_data_quality


def t(tid, front=None, back=None, day="2026-08-01", cost=2.0, lottery="dlt"):
    return {"ticket_id": tid, "lottery": lottery,
            "front": front or [1, 2, 3, 4, 5], "back": back or [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- 干净数据 ----------
def test_clean():
    rep = check_data_quality([t("T1", front=[1, 2, 3, 4, 5]),
                              t("T2", front=[6, 7, 8, 9, 10])])
    assert rep.duplicates == 0
    assert rep.issue_count == 0
    assert rep.trust_level == "A"


def test_empty():
    rep = check_data_quality([])
    assert rep.trust_level == "A"


# ---------- 重复票 ----------
def test_duplicates():
    rep = check_data_quality([t("T1"), t("T2"), t("T3")])
    assert rep.duplicates == 2
    assert rep.trust_level == "C"


def test_no_duplicates():
    tickets = [t(f"T{i}", front=[i + 1, i + 2, i + 3, i + 4, i + 5]) for i in range(3)]
    rep = check_data_quality(tickets)
    assert rep.duplicates == 0


# ---------- 错误号码 ----------
def test_invalid_count():
    rep = check_data_quality([t("T1", front=[1, 2, 3, 4])])
    assert rep.invalid_numbers == 1


def test_invalid_range():
    rep = check_data_quality([t("T1", front=[1, 2, 3, 4, 99])])
    assert rep.invalid_numbers == 1


def test_invalid_back():
    rep = check_data_quality([t("T1", back=[1, 99])])
    assert rep.invalid_numbers == 1


# ---------- 日期异常 ----------
def test_future_date():
    future = (date.today() + timedelta(days=10)).isoformat()
    rep = check_data_quality([t("T1", day=future)])
    assert rep.date_anomalies == 1


def test_bad_date_format():
    rep = check_data_quality([t("T1", day="2026/08/01")])
    assert rep.date_anomalies == 1


def test_good_date():
    rep = check_data_quality([t("T1", day="2026-08-01")])
    assert rep.date_anomalies == 0


# ---------- 金额异常 ----------
def test_zero_cost():
    rep = check_data_quality([t("T1", cost=0)])
    assert rep.amount_anomalies == 1


def test_huge_cost():
    rep = check_data_quality([t("T1", cost=99999)])
    assert rep.amount_anomalies == 1


# ---------- 彩种错误 ----------
def test_lottery_error_ssq():
    rep = check_data_quality([t("T1", front=[1, 2, 3, 4, 5, 34], back=[7], lottery="ssq")])
    assert rep.lottery_errors == 1


# ---------- 可信等级 ----------
def test_level_a():
    rep = check_data_quality([t("T1"), t("T2", front=[3, 4, 5, 6, 7])])
    assert rep.trust_level == "A"


def test_level_b():
    # 少量问题（1/20，不同号码）
    tickets = [t(f"T{i}", front=[i + 1, i + 2, i + 3, i + 4, i + 5]) for i in range(19)] + \
              [t("Tbad", front=[1, 2, 3, 4])]
    rep = check_data_quality(tickets)
    assert rep.trust_level == "B"


def test_level_c():
    rep = check_data_quality([t("T1"), t("T2")])
    assert rep.trust_level == "C"


# ---------- 结构 ----------
def test_to_dict():
    rep = check_data_quality([t("T1"), t("T2")])
    d = rep.to_dict()
    assert d["trust_level"] == "C"
    assert d["duplicates"] == 1


def test_summary_text():
    rep = check_data_quality([t("T1")])
    assert "数据质量" in rep.summary_text()
    assert "可信等级" in rep.summary_text()


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n_dup", range(0, 8))
def test_dup_scale(n_dup):
    tickets = [t(f"T{i}") for i in range(n_dup + 1)]
    rep = check_data_quality(tickets)
    assert rep.duplicates == n_dup


@pytest.mark.parametrize("i", range(10))
def test_clean_matrix(i):
    tickets = [t(f"T{j}", front=[j + 1, j + 2, j + 3, j + 4, j + 5]) for j in range(i + 1)]
    rep = check_data_quality(tickets)
    assert rep.trust_level in ("A", "B")
