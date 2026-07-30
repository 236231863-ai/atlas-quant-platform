"""Atlas Quant Platform - Strategy Tournament.

Compares multiple strategies and generates ranking reports.
Pure computation: no IO, no database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.types.models import DrawRecordData
from engine.backtest.models import BacktestConfig, TradeRecord, BacktestMetrics
from engine.backtest.simulator import TradeSimulator
from engine.backtest.analyzers import ResultAggregator
from engine.strategy.registry import StrategyDefinition


@dataclass
class StrategyResult:
    """Result of one strategy in a tournament."""
    rank: int
    strategy_id: str
    strategy_name: str
    strategy_type: str
    metrics: BacktestMetrics
    trade_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "strategy_type": self.strategy_type,
            "trade_count": self.trade_count,
            "roi": self.metrics.roi,
            "win_rate": self.metrics.win_rate,
            "sharpe_ratio": self.metrics.sharpe_ratio,
            "max_drawdown_pct": self.metrics.max_drawdown_pct,
            "volatility": self.metrics.volatility,
        }


@dataclass
class TournamentResult:
    """Complete tournament ranking."""
    results: List[StrategyResult]
    total_strategies: int
    ranking_metric: str
    config: Dict[str, Any]
    best_strategy_id: str

    def generate_markdown(self) -> str:
        """Generate ranking report in Markdown."""
        lines = [
            "# Strategy Tournament Ranking",
            "",
            f"**Total Strategies**: {self.total_strategies}",
            f"**Ranking Metric**: {self.ranking_metric}",
            f"**Config**: {self.config}",
            "",
            "## Ranking",
            "",
            "| Rank | Strategy | Type | ROI | Win Rate | Sharpe | Max DD | Volatility |",
            "|------|----------|------|-----|----------|--------|--------|------------|",
        ]
        for r in self.results:
            lines.append(
                f"| {r.rank} | {r.strategy_name} | {r.strategy_type} | "
                f"{r.metrics.roi:.2f}% | {r.metrics.win_rate:.2f}% | "
                f"{r.metrics.sharpe_ratio:.4f} | {r.metrics.max_drawdown_pct:.2f}% | "
                f"{r.metrics.volatility:.4f} |"
            )
        lines.append("")
        lines.append(f"**Winner**: {self.best_strategy_id}")
        return "\n".join(lines)


class StrategyTournament:
    """Runs automatic comparison of multiple strategies."""

    def __init__(self) -> None:
        self._simulator = TradeSimulator()
        self._aggregator = ResultAggregator()

    def run(
        self,
        draws: List[DrawRecordData],
        config: BacktestConfig,
        strategies: List[StrategyDefinition],
        ranking_metric: str = "sharpe_ratio",
    ) -> TournamentResult:
        """Run tournament comparing multiple strategies.

        Args:
            draws: Historical draw data.
            config: Base backtest config (strategy_id will be overridden per run).
            strategies: List of strategies to compare.
            ranking_metric: Metric to rank by.

        Returns:
            TournamentResult with ranked strategies.
        """
        results: List[StrategyResult] = []

        for i, strategy in enumerate(strategies):
            # Create per-strategy config
            strat_config = BacktestConfig(
                lottery_code=config.lottery_code,
                strategy_id=strategy.strategy_id,
                start_date=config.start_date,
                end_date=config.end_date,
                main_range=config.main_range,
                main_count=config.main_count,
                bonus_range=config.bonus_range,
                bonus_count=config.bonus_count,
                initial_capital=config.initial_capital,
                bet_per_draw=config.bet_per_draw,
                random_seed=config.random_seed,
            )

            trades = self._simulator.run(draws, strat_config)
            metrics = self._aggregator.analyze(trades)

            results.append(StrategyResult(
                rank=0,
                strategy_id=strategy.strategy_id,
                strategy_name=strategy.name,
                strategy_type=strategy.strategy_type,
                metrics=metrics,
                trade_count=len(trades),
            ))

        # Rank by metric (descending)
        results.sort(key=lambda r: getattr(r.metrics, ranking_metric, 0), reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1

        best_id = results[0].strategy_id if results else ""
        return TournamentResult(
            results=results,
            total_strategies=len(strategies),
            ranking_metric=ranking_metric,
            config=config.to_dict(),
            best_strategy_id=best_id,
        )
