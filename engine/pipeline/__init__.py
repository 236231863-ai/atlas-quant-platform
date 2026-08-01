"""Data ingestion, validation, and backup pipeline."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import date

from core.types.models import DrawRecordData


@dataclass
class IngestionReport:
    total: int = 0; imported: int = 0; skipped: int = 0; errors: List[str] = field(default_factory=list)
    def to_dict(self):
        return {"total":self.total,"imported":self.imported,"skipped":self.skipped,"errors":self.errors}

class DataIngestionPipeline:
    def __init__(self, plugin):
        self._plugin = plugin
    def get_game_def(self):
        return self._plugin.get_lottery_type()

class DataValidator:
    @staticmethod
    def validate_draw(draw: DrawRecordData, main_range: Tuple[int,int], main_count: int,
                      bonus_range: Optional[Tuple[int,int]]=None, bonus_count: int=0) -> List[str]:
        errors = []
        if len(draw.main_numbers) != main_count: errors.append(f"Expected {main_count} main numbers, got {len(draw.main_numbers)}")
        if draw.bonus_numbers and bonus_range and len(draw.bonus_numbers) != bonus_count:
            errors.append(f"Expected {bonus_count} bonus numbers, got {len(draw.bonus_numbers)}")
        for n in draw.main_numbers:
            if n < main_range[0] or n > main_range[1]: errors.append(f"Main number {n} out of range {main_range}")
        if draw.bonus_numbers and bonus_range:
            for n in draw.bonus_numbers:
                if n < bonus_range[0] or n > bonus_range[1]: errors.append(f"Bonus number {n} out of range {bonus_range}")
        return errors

    @staticmethod
    def validate_batch(draws: List[DrawRecordData], **kwargs) -> List[Tuple[DrawRecordData, List[str]]]:
        return [(d, DataValidator.validate_draw(d, **kwargs)) for d in draws]


class BackupManager:
    @staticmethod
    def create_backup_plan(dest: str = "data/backups") -> Dict[str, Any]:
        return {"destination": dest, "tables": ["lottery_games","draw_records","strategy_runs"], "format": "sql", "compression": "gzip"}
