"""v4.8 大规模矩阵 1：import/ocr 纯计算参数化。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.import_center import TextImporter, import_text
from engine.ticket_ocr import parse_ocr_text, TicketOCREngine


def nums_text(front, back):
    return " ".join(f"{n:02d}" for n in front) + " + " + " ".join(f"{n:02d}" for n in back)


# ---------- import 纯计算 ----------
@pytest.mark.parametrize("i", range(40))
def test_text_parse_front_back(i):
    t = TextImporter.parse(f"{i+1:02d} 05 12 23 30 + 06 08")
    assert t["front"][0] == i + 1


@pytest.mark.parametrize("i", range(30))
def test_text_parse_ssq(i):
    t = TextImporter.parse(f"{i+1:02d} 02 03 04 05 06 07", lottery="ssq")
    assert len(t["front"]) == 6
    assert t["back"] == [7]


@pytest.mark.parametrize("n", range(1, 21))
def test_import_scale(ticket_storage, n):
    lines = "\n".join(f"{i+1:02d} 05 12 23 30 + 06 08" for i in range(n))
    rep = import_text(lines)
    assert rep.total_imported == n


@pytest.mark.parametrize("i", range(20))
def test_import_empty_lines(ticket_storage, i):
    rep = import_text("bad\n\n\n")
    assert rep.total_imported == 0


# ---------- OCR 纯计算 ----------
@pytest.mark.parametrize("i", range(40))
def test_ocr_front_back(i):
    front = [1, 2, 3, 4, 5]
    back = [i % 12 + 1, (i + 3) % 12 + 1]
    r = parse_ocr_text(nums_text(front, back))
    assert len(r.front) == 5
    assert len(r.back) == 2


@pytest.mark.parametrize("i", range(30))
def test_ocr_ssq(i):
    r = parse_ocr_text(f"{i+1:02d} 02 03 04 05 06 07", lottery="ssq")
    assert len(r.front) == 6
    assert r.back == [7]


@pytest.mark.parametrize("i", range(30))
def test_ocr_amount(i):
    r = parse_ocr_text(f"01 05 12 23 30 06 08 ¥{i * 2}")
    assert r.amount == i * 2


@pytest.mark.parametrize("i", range(30))
def test_ocr_date(i):
    d = (date.today() - timedelta(days=i)).isoformat()
    r = parse_ocr_text(f"01 05 12 23 30 06 08 {d}")
    assert r.draw_date == d


@pytest.mark.parametrize("i", range(20))
def test_ocr_confirm_edit(ticket_storage, i):
    r = parse_ocr_text(f"01 05 12 23 30 06 08")
    r2 = TicketOCREngine.confirm(r, back=[i % 12 + 1, 2])
    assert r2.back[0] == i % 12 + 1
    assert r2.confirmed
