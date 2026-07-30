"""Atlas Quant Platform - Feature Engine.

Numerical feature generation from historical draw data.
All features are pure computations: no IO, no database.
"""
from __future__ import annotations

from engine.features.frequency_features import compute_frequency_features
from engine.features.gap_features import compute_gap_features
from engine.features.distribution_features import compute_distribution_features
from engine.features.entropy_features import compute_entropy_features
from engine.features.pair_features import compute_pair_features

__all__ = [
    "compute_frequency_features",
    "compute_gap_features",
    "compute_distribution_features",
    "compute_entropy_features",
    "compute_pair_features",
]
