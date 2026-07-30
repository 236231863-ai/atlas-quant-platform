"""
Atlas Quant Platform - Error Framework.

统一的异常层次结构。
"""
from __future__ import annotations

from typing import Optional

from core.types import ErrorCode


class AtlasError(Exception):
    """所有平台异常的基类"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[str] = None,
    ) -> None:
        self.code = code
        self.details = details
        super().__init__(message)

    @property
    def message(self) -> str:
        return str(self.args[0]) if self.args else ""


# ---- 数据层异常 ----
class DataError(AtlasError):
    """数据层异常基类"""


class DataSourceUnavailableError(DataError):
    def __init__(self, source: str, reason: str) -> None:
        super().__init__(
            code=ErrorCode.DATA_SOURCE_UNAVAILABLE,
            message=f"Data source '{source}' unavailable: {reason}",
        )


class DataIntegrityError(DataError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            code=ErrorCode.DATA_INTEGRITY_ERROR,
            message=f"Data integrity check failed: {detail}",
        )


class InsufficientDataError(DataError):
    def __init__(self, required: int, available: int) -> None:
        super().__init__(
            code=ErrorCode.INSUFFICIENT_DATA,
            message=f"Insufficient data: need {required}, have {available}",
        )


# ---- 引擎层异常 ----
class EngineError(AtlasError):
    """引擎层异常基类"""


class InvalidBacktestConfigError(EngineError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            code=ErrorCode.INVALID_BACKTEST_CONFIG,
            message=f"Invalid backtest configuration: {detail}",
        )


class BacktestInterruptedError(EngineError):
    def __init__(self, reason: str) -> None:
        super().__init__(
            code=ErrorCode.BACKTEST_INTERRUPTED,
            message=f"Backtest interrupted: {reason}",
        )


class InvalidStrategyError(EngineError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            code=ErrorCode.INVALID_STRATEGY,
            message=f"Invalid strategy: {detail}",
        )


# ---- 验证层异常 ----
class ValidationError(AtlasError):
    """输入验证异常"""

    def __init__(self, detail: str, field: Optional[str] = None) -> None:
        msg = f"Validation error{f' on field {field}' if field else ''}: {detail}"
        super().__init__(code=ErrorCode.VALIDATION_ERROR, message=msg)
        self.field = field
