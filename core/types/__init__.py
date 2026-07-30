"""
Atlas Quant Platform - Core Type Definitions.

所有模块共享的基础类型。
不依赖任何框架，纯Python标准库。
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Sequence, TypeVar


# ---- 基础类型 ----
EntityId = uuid.UUID
"""实体ID类型"""

Timestamp = datetime
"""时间戳类型"""

DateRange = tuple[date, date]
"""日期范围 (start, end)"""

JsonDict = Dict[str, Any]
"""JSON字典类型"""

T = TypeVar("T")
"""通用类型变量"""


# ---- 枚举 ----
class AnalysisType(str, Enum):
    """分析类型"""
    FREQUENCY = "frequency"
    GAP = "gap"
    TREND = "trend"
    DISTRIBUTION = "distribution"
    COMPREHENSIVE = "comprehensive"


class BacktestStatus(str, Enum):
    """回测状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StrategyType(str, Enum):
    """策略类型"""
    FILTER = "filter"
    WEIGHTED = "weighted"
    COMBINATION = "combination"


class PluginState(str, Enum):
    """插件状态"""
    REGISTERED = "registered"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


# ---- 值对象 ----
@dataclass(frozen=True)
class NumberRange:
    """号码范围"""
    min_value: int
    max_value: int
    count: int

    def __post_init__(self) -> None:
        if self.min_value >= self.max_value:
            raise ValueError(f"min_value ({self.min_value}) must be < max_value ({self.max_value})")
        if self.count <= 0:
            raise ValueError(f"count ({self.count}) must be positive")
        if self.count > (self.max_value - self.min_value + 1):
            raise ValueError(f"count ({self.count}) exceeds range size")


@dataclass(frozen=True)
class LotteryTypeDef:
    """彩种定义"""
    code: str
    name: str
    region: str
    main_range: NumberRange
    bonus_range: Optional[NumberRange] = None


@dataclass(frozen=True)
class AnalysisWindow:
    """分析窗口"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    draw_count: Optional[int] = None

    def __post_init__(self) -> None:
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        if self.draw_count is not None and self.draw_count <= 0:
            raise ValueError("draw_count must be positive")


@dataclass(frozen=True)
class FundConfig:
    """资金配置"""
    initial_capital: Decimal
    bet_per_draw: Decimal
    max_daily_bet: Optional[Decimal] = None
    max_drawdown_limit: Optional[Decimal] = None

    def __post_init__(self) -> None:
        if self.initial_capital <= Decimal("0"):
            raise ValueError("initial_capital must be positive")
        if self.bet_per_draw <= Decimal("0"):
            raise ValueError("bet_per_draw must be positive")


# ---- 异常码 ----
class ErrorCode(str, Enum):
    """错误码枚举"""
    # 通用
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"

    # 数据
    DATA_SOURCE_UNAVAILABLE = "DATA_SOURCE_UNAVAILABLE"
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

    # 回测
    INVALID_BACKTEST_CONFIG = "INVALID_BACKTEST_CONFIG"
    BACKTEST_INTERRUPTED = "BACKTEST_INTERRUPTED"

    # 策略
    INVALID_STRATEGY = "INVALID_STRATEGY"
    STRATEGY_VERSION_CONFLICT = "STRATEGY_VERSION_CONFLICT"

    # 速率
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
