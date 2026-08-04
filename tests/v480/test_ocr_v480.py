"""v4.8 P2：彩票票面 OCR 识别测试。

覆盖：解析 / 日期金额提取 / 人工确认流程 / 未确认禁止保存。
"""
from __future__ import annotations

import pytest

from engine.ticket_ocr import OCRResult, TicketOCREngine, parse_ocr_text


# ---------- 解析 ----------
def test_parse_basic():
    r = parse_ocr_text("大乐透 01 05 12 23 30 + 06 08")
    assert r.front == [1, 5, 12, 23, 30]
    assert r.back == [6, 8]


def test_parse_ssq():
    r = parse_ocr_text("双色球 01 02 03 04 05 06 07", lottery="ssq")
    assert len(r.front) == 6
    assert r.back == [7]


def test_parse_empty():
    r = parse_ocr_text("")
    assert r.front == []
    assert r.back == []


def test_parse_date():
    r = parse_ocr_text("01 05 12 23 30 06 08 2026-08-01")
    assert r.draw_date == "2026-08-01"


def test_parse_date_slash():
    r = parse_ocr_text("01 05 12 23 30 06 08 2026/8/1")
    assert r.draw_date == "2026-8-1"


def test_parse_amount():
    r = parse_ocr_text("01 05 12 23 30 06 08 ¥2")
    assert r.amount == 2.0


# ---------- 确认流程 ----------
def test_needs_confirmation():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    assert r.needs_confirmation is True


def test_confirm_sets_flag():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    r2 = TicketOCREngine.confirm(r)
    assert r2.confirmed is True


def test_confirm_edit():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    r2 = TicketOCREngine.confirm(r, front=[1, 5, 12, 23, 30], back=[6, 9])
    assert r2.back == [6, 9]


# ---------- 保存 ----------
def test_save_unconfirmed_rejected(ticket_storage):
    r = parse_ocr_text("01 05 12 23 30 06 08")
    assert TicketOCREngine.save_confirmed(r) is False


def test_save_confirmed(ticket_storage):
    r = parse_ocr_text("01 05 12 23 30 06 08")
    r2 = TicketOCREngine.confirm(r)
    assert TicketOCREngine.save_confirmed(r2) is True
    from engine.ticket_system import TicketManager
    assert TicketManager().count() == 1


def test_save_invalid_confirmed(ticket_storage):
    r = parse_ocr_text("01 02 03")
    r2 = TicketOCREngine.confirm(r)
    assert TicketOCREngine.save_confirmed(r2) is False


# ---------- 结构 ----------
def test_result_valid():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    assert r.valid is True


def test_result_invalid():
    r = parse_ocr_text("01 02 03")
    assert r.valid is False


def test_result_to_dict():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    d = r.to_dict()
    assert d["confirmed"] is False
    assert d["valid"] is True


def test_result_summary():
    r = parse_ocr_text("01 05 12 23 30 06 08")
    assert "待确认" in r.summary_text()
    r.confirmed = True
    assert "已确认" in r.summary_text()


def test_engine_field():
    r = TicketOCREngine.parse_ocr_text("01 05 12 23 30 06 08", engine="tesseract")
    assert r.engine == "tesseract"


# ---------- 矩阵 ----------
@pytest.mark.parametrize("i", range(10))
def test_parse_random(i):
    import random
    random.seed(i)
    nums = random.sample(range(1, 36), 5) + random.sample(range(1, 13), 2)
    text = " ".join(f"{n:02d}" for n in nums)
    r = parse_ocr_text(text)
    assert r.valid is True
    assert len(r.front) == 5
    assert len(r.back) == 2


@pytest.mark.parametrize("i", range(10))
def test_confirm_save_loop(ticket_storage, i):
    r = parse_ocr_text(f"01 05 12 23 30 06 08")
    r2 = TicketOCREngine.confirm(r)
    assert TicketOCREngine.save_confirmed(r2) is True
