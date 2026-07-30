"""Anomaly Detector - detects unusual distributions, overfitting, abnormal behavior."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats as scipy_stats

from core.types.models import DrawRecordData
from engine.backtest.models import BacktestMetrics, TradeRecord


@dataclass
class AnomalyReport:
    """Report of detected anomalies."""
    has_anomalies: bool
    total_checks: int
    anomaly_count: int
    anomalies: List[Dict[str, Any]]
    overall_assessment: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnomalyDetector:
    """Detects statistical anomalies in draw data and strategy behavior.

    Pure computation: statistical tests and pattern analysis.
    """

    def detect_distribution_anomalies(
        self,
        draws: List[DrawRecordData],
        main_range: Tuple[int, int],
        significance_level: float = 0.05,
    ) -> AnomalyReport:
        """Detect unusual distributions in draw data.

        Uses chi-square test to detect if number distribution
        deviates significantly from uniform expectation.
        """
        if not draws or len(draws) < 5:
            return AnomalyReport(
                has_anomalies=False, total_checks=1, anomaly_count=0,
                anomalies=[], overall_assessment="Insufficient data for analysis.",
            )

        min_v, max_v = main_range
        range_size = max_v - min_v + 1

        # Count frequencies
        counter: Counter[int] = Counter()
        for d in draws:
            counter.update(d.main_numbers)

        observed: List[float] = []
        for n in range(min_v, max_v + 1):
            observed.append(float(counter.get(n, 0)))

        # Chi-square test for uniformity
        total = sum(observed)
        expected = [total / range_size] * range_size

        anomalies: List[Dict[str, Any]] = []

        try:
            chi2_stat, p_value = scipy_stats.chisquare(observed, expected)
            if p_value < significance_level:
                # Find which numbers deviate most
                max_deviation = 0
                max_dev_num = 0
                for n in range(range_size):
                    dev = abs(observed[n] - expected[n])
                    if dev > max_deviation:
                        max_deviation = dev
                        max_dev_num = n + min_v
                anomalies.append({
                    "type": "distribution_anomaly",
                    "severity": "high",
                    "detail": f"Number distribution deviates from uniform (p={p_value:.4f}). "
                              f"Number {max_dev_num} shows highest deviation.",
                    "chi_square": round(chi2_stat, 2),
                    "p_value": round(p_value, 4),
                })
        except Exception:
            pass

        # Detect streak anomalies (same number appearing too frequently)
        max_count = max(observed) if observed else 0
        min_count = min(observed) if observed else 0
        range_ratio = max_count / min_count if min_count > 0 else float("inf")

        if range_ratio > 5:
            max_num = observed.index(max(observed)) + min_v
            min_num = observed.index(min(observed)) + min_v
            anomalies.append({
                "type": "frequency_imbalance",
                "severity": "medium",
                "detail": f"Large frequency imbalance: number {max_num} appears {max_count}x, "
                          f"number {min_num} appears {min_count}x (ratio: {range_ratio:.1f}).",
            })

        # Detect consecutive same-number patterns (lottery machine anomaly)
        for n in range(min_v, max_v + 1):
            streak = 0
            max_streak = 0
            for d in draws:
                if n in d.main_numbers:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 0
            if max_streak >= 3:
                anomalies.append({
                    "type": "consecutive_appearance",
                    "severity": "low",
                    "detail": f"Number {n} appeared in {max_streak} consecutive draws.",
                    "streak": max_streak,
                })

        return AnomalyReport(
            has_anomalies=len(anomalies) > 0,
            total_checks=3,
            anomaly_count=len(anomalies),
            anomalies=anomalies,
            overall_assessment=self._assess_distribution(anomalies),
        )

    def detect_overfitting(
        self,
        train_metrics: BacktestMetrics,
        test_metrics: BacktestMetrics,
    ) -> AnomalyReport:
        """Detect overfitting by comparing training vs test performance.

        Args:
            train_metrics: Backtest metrics on training data.
            test_metrics: Backtest metrics on test/validation data.

        Returns:
            Anomaly report with overfitting indicators.
        """
        anomalies: List[Dict[str, Any]] = []
        total_checks = 3

        # Check 1: Large performance drop
        roi_diff = abs(train_metrics.roi - test_metrics.roi)
        if roi_diff > 50:
            anomalies.append({
                "type": "overfitting",
                "severity": "high",
                "detail": f"Large performance gap: training ROI={train_metrics.roi:.1f}%, "
                          f"test ROI={test_metrics.roi:.1f}% (gap={roi_diff:.1f}%). Overfitting likely.",
                "roi_gap": round(roi_diff, 1),
            })

        # Check 2: Win rate drop
        wr_diff = abs(train_metrics.win_rate - test_metrics.win_rate)
        if wr_diff > 20:
            anomalies.append({
                "type": "win_rate_instability",
                "severity": "medium",
                "detail": f"Win rate difference of {wr_diff:.1f}% between training and test sets.",
                "win_rate_gap": round(wr_diff, 1),
            })

        # Check 3: Sharpe ratio collapse
        sharpe_diff = abs(train_metrics.sharpe_ratio - test_metrics.sharpe_ratio)
        if sharpe_diff > 1.0:
            anomalies.append({
                "type": "risk_profile_change",
                "severity": "medium",
                "detail": f"Sharpe ratio changed by {sharpe_diff:.2f} between train/test. "
                          f"Risk profile is not stable.",
                "sharpe_gap": round(sharpe_diff, 2),
            })
        elif train_metrics.sharpe_ratio > 1.5 and test_metrics.sharpe_ratio < 0:
            anomalies.append({
                "type": "overfitting",
                "severity": "high",
                "detail": f"Training Sharpe={train_metrics.sharpe_ratio:.2f} but test Sharpe={test_metrics.sharpe_ratio:.2f}. "
                          f"Strong overfitting indicator.",
            })

        has_anomalies = len(anomalies) > 0
        assessment = "Overfitting detected" if has_anomalies else "No significant overfitting indicators"

        return AnomalyReport(
            has_anomalies=has_anomalies,
            total_checks=total_checks,
            anomaly_count=len(anomalies),
            anomalies=anomalies,
            overall_assessment=assessment,
        )

    def detect_strategy_anomalies(
        self,
        trades: List[TradeRecord],
        metrics: BacktestMetrics,
    ) -> AnomalyReport:
        """Detect abnormal strategy behavior.

        Args:
            trades: Trade records.
            metrics: Backtest metrics.

        Returns:
            Anomaly report with strategy behavior anomalies.
        """
        anomalies: List[Dict[str, Any]] = []

        # Check for long losing streaks
        if metrics.max_consecutive_losses > 10:
            anomalies.append({
                "type": "extreme_losing_streak",
                "severity": "high",
                "detail": f"Strategy experienced {metrics.max_consecutive_losses} consecutive losses. "
                          f"May indicate strategy failure regime.",
                "streak_length": metrics.max_consecutive_losses,
            })

        # Check for extreme single wins
        if metrics.best_single_return > metrics.total_investment * 0.5:
            anomalies.append({
                "type": "return_concentration",
                "severity": "medium",
                "detail": f"Single trade return (${metrics.best_single_return:.0f}) represents "
                          f"more than 50% of total investment. Returns are concentrated.",
            })

        # Check if most wins are low prize
        if trades:
            wins = [t for t in trades if t.is_win]
            if wins:
                low_prize_wins = sum(1 for t in wins if t.prize_level > 8)
                low_prize_pct = low_prize_wins / len(wins) * 100
                if low_prize_pct > 80:
                    anomalies.append({
                        "type": "low_value_wins",
                        "severity": "low",
                        "detail": f"{low_prize_pct:.0f}% of wins are low-value prizes (level 9+). "
                                  f"Wins do not cover bet costs.",
                        "low_prize_pct": round(low_prize_pct, 1),
                    })

        return AnomalyReport(
            has_anomalies=len(anomalies) > 0,
            total_checks=3,
            anomaly_count=len(anomalies),
            anomalies=anomalies,
            overall_assessment=self._assess_strategy_anomalies(anomalies),
        )

    def _assess_distribution(self, anomalies: List[Dict[str, Any]]) -> str:
        if not anomalies:
            return "Number distribution appears normal."
        high = sum(1 for a in anomalies if a["severity"] == "high")
        if high > 0:
            return f"Found {high} high-severity distribution anomalies requiring attention."
        return f"Found {len(anomalies)} minor distribution anomalies."

    def _assess_strategy_anomalies(self, anomalies: List[Dict[str, Any]]) -> str:
        if not anomalies:
            return "Strategy behavior is within normal parameters."
        return f"Found {len(anomalies)} strategy anomalies to review."
