"""
Atlas Quant Platform - TradeSimulator.

Walk-forward simulation engine. Prevents future data leakage.
Pure computation: no IO, no database, no side effects.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData
from engine.backtest.models import TradeRecord, BacktestConfig
from engine.strategy.evaluator import StrategyEvaluator


# Default prize table for DLT (大乐透)
# Key: "matched_main:matched_bonus", Value: prize amount
DEFAULT_PRIZE_TABLE: Dict[str, float] = {
    "5:2": 5000000.00,   # Level 1 - Jackpot
    "5:1": 200000.00,    # Level 2
    "5:0": 10000.00,     # Level 3
    "4:2": 3000.00,      # Level 4
    "4:1": 300.00,       # Level 5
    "3:2": 200.00,       # Level 6
    "4:0": 100.00,       # Level 7
    "3:1": 15.00,        # Level 8
    "2:2": 5.00,         # Level 9
    "3:0": 5.00,         # Level 10
    "1:2": 5.00,         # Level 11
    "2:1": 5.00,         # Level 12
}


class TradeSimulator:
    """Walk-forward backtest simulator.

    Simulates trading through historical data one draw at a time.
    At each step, only data up to that point is used (no future leakage).
    """

    def __init__(
        self,
        prize_table: Optional[Dict[str, float]] = None,
    ) -> None:
        self._prize_table = prize_table or DEFAULT_PRIZE_TABLE
        self._evaluator = StrategyEvaluator()

    def run(
        self,
        draws: List[DrawRecordData],
        config: BacktestConfig,
    ) -> List[TradeRecord]:
        """Run a walk-forward simulation.

        Args:
            draws: Chronologically ordered list of draw records.
            config: Backtest configuration.

        Returns:
            List of trade records for every simulated draw.

        Raises:
            ValueError: If draws are empty or config is invalid.
        """
        if not draws:
            return []

        self._validate_config(config)
        rng = random.Random(config.random_seed)
        trades: List[TradeRecord] = []
        capital = config.initial_capital
        cumulative_pnl = 0.0

        for i, current_draw in enumerate(draws):
            # Walk-forward: only use data up to (but not including) current draw
            history = draws[:i]

            # Evaluate strategy against historical data
            try:
                bet_main, bet_bonus = self._evaluator.evaluate(
                    history=history,
                    main_range=config.main_range,
                    main_count=config.main_count,
                    bonus_range=config.bonus_range,
                    bonus_count=config.bonus_count,
                    rng=rng,
                )
            except Exception:
                # Skip this draw if strategy evaluation fails
                continue

            if not bet_main:
                continue

            # Record the trade
            matched_main = self._count_matches(
                bet_main, current_draw.main_numbers
            )
            matched_bonus = 0
            if bet_bonus and current_draw.bonus_numbers:
                matched_bonus = self._count_matches(
                    bet_bonus, current_draw.bonus_numbers
                )

            win_amount, prize_level = self._calculate_prize(
                matched_main, matched_bonus
            )

            is_win = win_amount > 0
            pnl = win_amount - config.bet_per_draw
            cumulative_pnl += pnl
            capital += pnl

            trade = TradeRecord(
                draw_date=str(current_draw.draw_date),
                draw_number=current_draw.draw_number,
                lottery_code=config.lottery_code,
                bet_main_numbers=bet_main,
                bet_bonus_numbers=bet_bonus,
                actual_main_numbers=current_draw.main_numbers,
                actual_bonus_numbers=current_draw.bonus_numbers,
                bet_amount=config.bet_per_draw,
                win_amount=win_amount,
                is_win=is_win,
                prize_level=prize_level,
                matched_main=matched_main,
                matched_bonus=matched_bonus,
                cumulative_pnl=round(cumulative_pnl, 2),
                cumulative_roi=round(
                    cumulative_pnl / config.initial_capital * 100, 2
                ) if config.initial_capital > 0 else 0.0,
            )
            trades.append(trade)

        return trades

    def _validate_config(self, config: BacktestConfig) -> None:
        """Validate backtest configuration."""
        if config.initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        if config.bet_per_draw <= 0:
            raise ValueError("bet_per_draw must be positive")
        if config.bet_per_draw > config.initial_capital:
            raise ValueError("bet_per_draw cannot exceed initial_capital")

    def _count_matches(
        self, bet: List[int], actual: List[int]
    ) -> int:
        """Count how many numbers match between bet and actual."""
        return len(set(bet) & set(actual))

    def _calculate_prize(
        self, matched_main: int, matched_bonus: int
    ) -> Tuple[float, int]:
        """Calculate prize amount and level based on matches.

        Args:
            matched_main: Number of matched main numbers.
            matched_bonus: Number of matched bonus numbers.

        Returns:
            Tuple of (prize_amount, prize_level).
        """
        key = f"{matched_main}:{matched_bonus}"
        # Find best matching prize level (walk up from exact match)
        for m in range(matched_main, -1, -1):
            for b in range(matched_bonus, -1, -1):
                k = f"{m}:{b}"
                if k in self._prize_table:
                    amount = self._prize_table[k]
                    # Determine prize level by position in table
                    level = list(self._prize_table.keys()).index(k) + 1
                    return amount, level
        return 0.0, 0
