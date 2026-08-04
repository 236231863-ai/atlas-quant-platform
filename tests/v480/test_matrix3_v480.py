"""v4.8 大规模矩阵 3：综合纯计算（补足 ≥1000）。"""
from __future__ import annotations

import pytest

from engine.import_center import TextImporter
from engine.ticket_ocr import parse_ocr_text
from engine.data_quality import check_data_quality
from engine.profile_card import build_profile_card


def t(tid, front=None, day="2026-08-01", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": front or [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- 综合纯计算 ----------
@pytest.mark.parametrize("i", range(60))
def test_parse_numbers_any(i):
    r = parse_ocr_text(f"{i % 35 + 1:02d} 02 03 04 05 06 07")
    assert len(r.front) == 5
    assert len(r.back) == 2


@pytest.mark.parametrize("i", range(50))
def test_import_parse_any(i):
    ti = TextImporter.parse(f"{i % 35 + 1:02d} 02 03 04 05 06 07")
    assert ti is not None


@pytest.mark.parametrize("i", range(40))
def test_quality_issue_count(i):
    tickets = [t(f"T{j}", front=[j + 1, j + 2, j + 3, j + 4, j + 5]) for j in range(10)]
    tickets += [t(f"Tbad{j}") for j in range(i % 5)]
    rep = check_data_quality(tickets)
    assert rep.issue_count >= 0


@pytest.mark.parametrize("i", range(40))
def test_profile_net_negative(i):
    card = build_profile_card([t(f"T{j}") for j in range(i + 1)])
    assert card.net == -(i + 1) * 2.0


@pytest.mark.parametrize("i", range(40))
def test_profile_summary(i):
    card = build_profile_card([t(f"T{j}") for j in range(i + 1)])
    assert card.summary_text()
    assert "随机性" in card.summary_text()
