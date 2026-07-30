"""
Atlas Quant Platform - Backtest Models.

Pure data structures for backtesting. No framework dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class TradeRecord:
    """A single simulated trade during backtest."""
    draw_date: str
    draw_number: str
    lottery_code: str
    bet_main_numbers: List[int]
    bet_bonus_numbers: Optional[List[int]]
    actual_main_numbers: List[int]
    actual_bonus_numbers: Optional[List[int]]
    bet_amount: float
    win_amount: float = 0.0
    is_win: bool = False
    prize_level: int = 0
    matched_main: int = 0
    matched_bonus: int = 0
    cumulative_pnl: float = 0.0
    cumulative_roi: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    lottery_code: str
    strategy_id: str
    start_date: str
    end_date: str
    main_range: tuple = (1, 35)
    main_count: int = 5
    bonus_range: Optional[tuple] = None
    bonus_count: int = 0
    initial_capital: float = 10000.0
    bet_per_draw: float = 10.0
    random_seed: Optional[int] = None
    prize_table: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BacktestMetrics:
    """Calculated performance metrics from a backtest."""
    total_investment: float = 0.0
    total_return: float = 0.0
    roi: float = 0.0
    win_count: int = 0
    total_bets: int = 0
    win_rate: float = 0.0
    max_drawdown_amount: float = 0.0
    max_drawdown_pct: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    avg_return_per_bet: float = 0.0
    final_capital: float = 0.0
    prize_levels: Dict[str, int] = field(default_factory=dict)
    best_single_return: float = 0.0
    worst_single_return: float = 0.0
    consecutive_losses: int = 0
    max_consecutive_losses: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
