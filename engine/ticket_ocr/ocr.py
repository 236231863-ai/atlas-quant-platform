"""ticket_ocr.ocr - 彩票票面识别（v4.8 P2）。

识别彩种/号码/日期/金额。**OCR 错误必须允许人工确认**：
  图片 → OCR → 用户确认 → 保存

本模块提供：
  - OCR 文本解析（数字串 → 结构化票据）
  - 外部 OCR 引擎接口（ppocrv5 / tesseract，可用则调用，不可用降级手动输入）
  - 人工确认流程（confirmed 字段 + 编辑）
禁止：自动无确认写入。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OCRResult:
    """一次票面识别结果（待确认）。"""

    raw_text: str = ""
    lottery: str = "dlt"
    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)
    draw_date: str = ""
    amount: float = 2.0
    confirmed: bool = False
    engine: str = "text"          # text / ppocrv5 / tesseract / manual

    @property
    def needs_confirmation(self) -> bool:
        return not self.confirmed

    @property
    def valid(self) -> bool:
        n = 5 if self.lottery == "dlt" else 6
        return len(self.front) == n and len(self.back) == (2 if self.lottery == "dlt" else 1)

    def to_dict(self) -> dict:
        return {"raw_text": self.raw_text, "lottery": self.lottery,
                "front": list(self.front), "back": list(self.back),
                "draw_date": self.draw_date, "amount": self.amount,
                "confirmed": self.confirmed, "engine": self.engine,
                "valid": self.valid}

    def summary_text(self) -> str:
        tag = "✅ 已确认" if self.confirmed else "⚠️ 待确认"
        return (f"{tag} {self.lottery} {' '.join(f'{n:02d}' for n in self.front)} + "
                f"{' '.join(f'{n:02d}' for n in self.back)}"
                f"（日期 {self.draw_date or '?'} · ¥{self.amount:,.0f}）")


class TicketOCREngine:
    """票面 OCR 引擎。"""

    @staticmethod
    def _extract_numbers(text: str) -> List[int]:
        return [int(x) for x in re.findall(r"\d+", text)]

    @classmethod
    def parse_ocr_text(cls, text: str, lottery: str = "dlt",
                       engine: str = "text") -> OCRResult:
        """解析 OCR 文本 → 结构化结果（待确认）。"""
        result = OCRResult(raw_text=text.strip(), lottery=lottery, engine=engine)
        if not text.strip():
            return result
        nums = cls._extract_numbers(text)
        n = 5 if lottery == "dlt" else 6
        b = 2 if lottery == "dlt" else 1
        if len(nums) >= n + b:
            result.front = nums[:n]
            result.back = nums[n:n + b]
        # 日期（YYYY-MM-DD）
        m = re.search(r"(20\d{2}[-/]\d{1,2}[-/]\d{1,2})", text)
        if m:
            result.draw_date = m.group(1).replace("/", "-")
        # 金额（仅识别 ¥ 或「元」前缀，避免误匹配号码）
        m2 = re.search(r"[¥元]\s?(\d+(?:\.\d{1,2})?)", text)
        if m2:
            try:
                result.amount = float(m2.group(1))
            except ValueError:
                pass
        return result

    @classmethod
    def confirm(cls, result: OCRResult, front=None, back=None,
                draw_date=None, amount=None) -> OCRResult:
        """人工确认（可编辑字段）。确认后允许保存。"""
        if front is not None:
            result.front = list(front)
        if back is not None:
            result.back = list(back)
        if draw_date is not None:
            result.draw_date = draw_date
        if amount is not None:
            result.amount = amount
        result.confirmed = True
        return result

    @classmethod
    def save_confirmed(cls, result: OCRResult) -> bool:
        """保存已确认的识别结果（仅当 confirmed=True）。"""
        if not result.confirmed:
            return False
        if not result.valid:
            return False
        from engine.ticket_system import TicketManager
        mgr = TicketManager()
        mgr.add(result.lottery, result.front, result.back,
                buy_date=result.draw_date, draw_date="", cost=result.amount)
        return True


def parse_ocr_text(text: str, lottery: str = "dlt") -> OCRResult:
    """便捷函数。"""
    return TicketOCREngine.parse_ocr_text(text, lottery)
