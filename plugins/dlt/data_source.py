"""
Atlas Quant Platform - DLT Plugin Data Source.

大乐透 (Da Le Tou) data source adapter.
Handles CSV import, number validation, and domain object conversion.
"""
from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.types.models import DrawRecordData, LotteryGameData


DLT_GAME_DEF = LotteryGameData(
    code="dlt",
    name="大乐透",
    region="CN",
    main_range={"min": 1, "max": 35, "count": 5},
    bonus_range={"min": 1, "max": 12, "count": 2},
    draw_schedule="Mon,Wed,Sat",
)


class DltDataSource:
    """Data source adapter for 大乐透 (Da Le Tou) lottery."""

    def __init__(self) -> None:
        self.game = DLT_GAME_DEF

    def get_game_definition(self) -> LotteryGameData:
        return self.game

    def validate_numbers(self, main: List[int], bonus: Optional[List[int]] = None) -> bool:
        """Validate number ranges for DLT."""
        mr = self.game.main_range
        if len(main) != mr["count"]:
            return False
        if not all(mr["min"] <= n <= mr["max"] for n in main):
            return False
        if len(set(main)) != len(main):
            return False
        if bonus:
            br = self.game.bonus_range
            if len(bonus) != br["count"]:
                return False
            if not all(br["min"] <= n <= br["max"] for n in bonus):
                return False
            if len(set(bonus)) != len(bonus):
                return False
        return True

    def parse_csv_line(self, row: Dict[str, str]) -> DrawRecordData:
        """Parse a single CSV row into a DrawRecordData."""
        draw_number = row["draw_number"].strip()
        draw_date = date.fromisoformat(row["draw_date"].strip())
        main_numbers = [
            int(row[f"front_{i}"].strip()) for i in range(1, 6)
        ]
        bonus_numbers = [
            int(row[f"back_{i}"].strip()) for i in range(1, 3)
        ]
        pool_amount = None
        if "pool_amount" in row and row["pool_amount"].strip():
            pool_amount = Decimal(row["pool_amount"].strip())
        record = DrawRecordData(
            lottery_code="dlt",
            draw_number=draw_number,
            draw_date=draw_date,
            main_numbers=main_numbers,
            bonus_numbers=bonus_numbers,
            pool_amount=pool_amount,
        )
        if not self.validate_numbers(main_numbers, bonus_numbers):
            raise ValueError(f"Invalid numbers in draw {draw_number}: {main_numbers} / {bonus_numbers}")
        return record

    def parse_csv(self, content: str) -> List[DrawRecordData]:
        """Parse full CSV content into list of DrawRecordData."""
        reader = csv.DictReader(io.StringIO(content))
        records = []
        for row in reader:
            record = self.parse_csv_line(row)
            records.append(record)
        return records

    def parse_csv_file(self, path: str) -> List[DrawRecordData]:
        """Parse CSV file into list of DrawRecordData."""
        content = Path(path).read_text(encoding="utf-8")
        return self.parse_csv(content)
