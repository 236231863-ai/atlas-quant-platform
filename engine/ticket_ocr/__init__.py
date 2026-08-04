"""ticket_ocr - 彩票票面识别（v4.8 P2，人工确认）。"""
from engine.ticket_ocr.ocr import (
    OCRResult,
    TicketOCREngine,
    parse_ocr_text,
)

__all__ = ["OCRResult", "TicketOCREngine", "parse_ocr_text"]
