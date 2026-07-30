"""
Atlas Quant Platform - ORM Models.

SQLAlchemy 2.x ORM models for the data layer.
These are the persistence models, separate from domain types.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class LotteryGame(Base):
    """彩种定义表 - 存储彩种信息。"""
    __tablename__ = "lottery_games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[str] = mapped_column(String(20), nullable=False, default="CN")
    main_range: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    bonus_range: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    draw_schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    draws: Mapped[List["DrawRecord"]] = relationship(back_populates="game", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<LotteryGame(code='{self.code}', name='{self.name}')>"


class DrawRecord(Base):
    """开奖记录表 - 存储每期开奖结果。"""
    __tablename__ = "draw_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    lottery_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    draw_number: Mapped[str] = mapped_column(String(20), nullable=False)
    draw_date: Mapped[date] = mapped_column(Date, nullable=False)
    main_numbers: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    bonus_numbers: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    pool_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(15, 2), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    game_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("lottery_games.id"), nullable=True)
    game: Mapped[Optional["LotteryGame"]] = relationship(back_populates="draws")

    __table_args__ = (
        UniqueConstraint("lottery_code", "draw_number", name="uq_draw_per_lottery"),
        Index("idx_draw_lottery_date", "lottery_code", "draw_date"),
    )

    def __repr__(self) -> str:
        return f"<DrawRecord(code='{self.lottery_code}', number='{self.draw_number}')>"


class StrategyRun(Base):
    """策略运行记录表 - 存储回测运行记录。"""
    __tablename__ = "strategy_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    lottery_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    strategy_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    date_range_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_range_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    result_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return f"<StrategyRun(name='{self.name}', status='{self.status}')>"
