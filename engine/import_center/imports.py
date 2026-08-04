"""import_center.imports - 彩票数据导入中心（v4.8 P1）。

支持：
  1. 文本导入（号码串 → 票据）
  2. CSV 批量导入（日期/彩种/号码/金额）
  3. 历史票据导入（复用 ticket_system 去重）
输出 ImportReport。

复用 ticket_system 存储 + LotteryIntentParser 号码解析。
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import List, Optional

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class ImportReport:
    """导入结果报告。"""

    total_imported: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    tickets: List[dict] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return self.total_imported + self.duplicates + self.skipped + len(self.errors)

    def summary_text(self) -> str:
        lines = ["📥 导入完成"]
        lines.append(f"· 成功导入：{self.total_imported} 张")
        lines.append(f"· 重复跳过：{self.duplicates} 张")
        lines.append(f"· 无效跳过：{self.skipped} 张")
        if self.errors:
            lines.append(f"· 错误 {len(self.errors)} 条（已跳过）：")
            for e in self.errors[:5]:
                lines.append(f"  ⚠️ {e}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"total_imported": self.total_imported,
                "duplicates": self.duplicates, "skipped": self.skipped,
                "errors": list(self.errors)}


class TextImporter:
    """文本导入：号码串 → 票据。"""

    @staticmethod
    def parse(text: str, lottery: str = "dlt", buy_date: str = "") -> Optional[dict]:
        """解析一行号码文本。支持：
        01 05 12 23 30 + 06 08
        01 05 12 23 30 06 08
        01,05,12,23,30|06,08
        """
        if not text or not text.strip():
            return None
        try:
            from engine.lottery_intent.ticket_parser import TicketParser
            parsed = TicketParser.parse_single(text) if hasattr(TicketParser, "parse_single") else None
            if parsed:
                front, back = parsed
            else:
                front, back = TextImporter._manual_parse(text, lottery)
            if not front or not back:
                return None
            return {"lottery": lottery, "front": front, "back": back,
                    "buy_date": buy_date, "draw_date": "", "cost": 2.0}
        except Exception:
            return None

    @staticmethod
    def _manual_parse(text: str, lottery: str) -> tuple:
        import re
        nums = [int(x) for x in re.findall(r"\d+", text)]
        n = 5 if lottery == "dlt" else 6
        if len(nums) < n + (2 if lottery == "dlt" else 1):
            return [], []
        front = nums[:n]
        back = nums[n:n + (2 if lottery == "dlt" else 1)]
        return front, back

    @classmethod
    def import_text(cls, text: str, lottery: str = "dlt",
                    buy_date: str = "") -> ImportReport:
        """导入多行文本（每行一张票）。"""
        rep = ImportReport()
        lines = [l for l in text.splitlines() if l.strip()]
        if not lines:
            rep.skipped = 1
            return rep
        from engine.ticket_system import TicketManager
        mgr = TicketManager()
        for line in lines:
            ticket = cls.parse(line, lottery, buy_date)
            if not ticket:
                rep.skipped += 1
                continue
            added = mgr.add(ticket["lottery"], ticket["front"], ticket["back"],
                            buy_date=ticket["buy_date"], draw_date="",
                            cost=ticket["cost"])
            rep.tickets.append(added.__dict__)
            rep.total_imported += 1
        return rep


class CSVImporter:
    """CSV 批量导入：日期/彩种/号码/金额。"""

    HEADERS = ("date", "lottery", "numbers", "cost")

    @classmethod
    def import_csv(cls, path: str) -> ImportReport:
        """导入 CSV 文件。"""
        rep = ImportReport()
        if not os.path.exists(path):
            rep.errors.append(f"文件不存在：{path}")
            return rep
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):
                    numbers = (row.get("numbers") or "").strip()
                    lottery = (row.get("lottery") or "dlt").strip().lower()
                    date_s = (row.get("date") or "").strip()
                    cost_s = (row.get("cost") or "2").strip()
                    ticket = TextImporter.parse(numbers, lottery, date_s)
                    if not ticket:
                        rep.skipped += 1
                        rep.errors.append(f"第{i}行：号码无法解析")
                        continue
                    try:
                        ticket["cost"] = float(cost_s)
                    except ValueError:
                        ticket["cost"] = 2.0
                    from engine.ticket_system import TicketManager
                    t = TicketManager().add(ticket["lottery"], ticket["front"],
                                            ticket["back"], buy_date=date_s,
                                            draw_date="", cost=ticket["cost"])
                    rep.tickets.append(t.__dict__)
                    rep.total_imported += 1
        except Exception as e:  # noqa: BLE001
            rep.errors.append(f"CSV 读取失败：{e}")
        return rep


class HistoricalImporter:
    """历史票据导入：复用 ticket_system 已有票据（去重）。"""

    @classmethod
    def import_existing(cls) -> ImportReport:
        """从 ticket_system 已有票据导入（实际是去重统计）。"""
        from engine.ticket_system import TicketManager
        mgr = TicketManager()
        rep = ImportReport()
        rep.total_imported = mgr.count()
        return rep


def import_text(text: str, lottery: str = "dlt", buy_date: str = "") -> ImportReport:
    """便捷函数。"""
    return TextImporter.import_text(text, lottery, buy_date)


def import_csv(path: str) -> ImportReport:
    """便捷函数。"""
    return CSVImporter.import_csv(path)
