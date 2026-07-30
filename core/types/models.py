"""
Atlas Quant Platform - Domain Data Models.

Pure domain types for data transfer. No framework dependencies.
Used for inter-layer communication and API serialization.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class LotteryGameData:
    """Domain type for lottery game definition."""
    code: str
    name: str
    region: str = "CN"
    main_range: Optional[Dict[str, Any]] = None
    bonus_range: Optional[Dict[str, Any]] = None
    draw_schedule: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DrawRecordData:
    """Domain type for a single draw result."""
    lottery_code: str
    draw_number: str
    draw_date: date
    main_numbers: List[int]
    bonus_numbers: Optional[List[int]] = None
    pool_amount: Optional[Decimal] = None
    id: Optional[str] = None

    def validate_main_numbers(self, min_val: int, max_val: int, count: int) -> bool:
        if len(self.main_numbers) != count:
            return False
        return all(min_val <= n <= max_val for n in self.main_numbers)

    def validate_bonus_numbers(self, min_val: int, max_val: int, count: int) -> bool:
        if not self.bonus_numbers:
            return True
        if len(self.bonus_numbers) != count:
            return False
        return all(min_val <= n <= max_val for n in self.bonus_numbers)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["draw_date"] = str(self.draw_date)
        return result


@dataclass
class StrategyRunData:
    """Domain type for a strategy run."""
    name: str
    lottery_code: str
    strategy_json: Dict[str, Any]
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    status: str = "pending"
    result_summary: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.date_range_start:
            result["date_range_start"] = str(self.date_range_start)
        if self.date_range_end:
            result["date_range_end"] = str(self.date_range_end)
        return result


@dataclass
class DrawStatistics:
    """Statistics summary for a lottery."""
    lottery_code: str
    total_draws: int
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None
    latest_draw_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
