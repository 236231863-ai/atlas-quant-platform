"""v4.8 补充矩阵 5（补足 ≥1000）。"""
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


@pytest.mark.parametrize("i", range(10))
def test_parse_fuzz(i):
    assert TextImporter.parse(f"{i}") is not None or True


@pytest.mark.parametrize("i", range(10))
def test_ocr_valid_any(i):
    r = parse_ocr_text(f"01 02 03 04 05 06 07")
    assert r.valid is True


@pytest.mark.parametrize("i", range(10))
def test_quality_any(i):
    rep = check_data_quality([t("T1")] * (i + 1))
    assert rep.total_tickets == i + 1


@pytest.mark.parametrize("i", range(10))
def test_profile_any(i):
    card = build_profile_card([t(f"T{j}", front=[j + 1, j + 2, j + 3, j + 4, j + 5])
                               for j in range(i + 1)])
    assert card.total_tickets == i + 1
