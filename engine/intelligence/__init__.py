"""Atlas Quant Platform - Intelligence Engine.

AI-assisted quantitative research layer.
Consumes structured data from Engine, produces research analysis.
Pure computation: no DB, no HTTP side effects.

Architecture:
  ResearchAgent    → Comprehensive backtest analysis
  ModelExplainer   → Strategy performance explanation
  StrategyAdvisor  → Improvement suggestions + risk warnings
  AnomalyDetector  → Statistical anomaly detection
"""
from __future__ import annotations

from engine.intelligence.research_agent import ResearchAgent, ResearchReport
from engine.intelligence.model_explainer import ModelExplainer, FeatureImportance
from engine.intelligence.strategy_advisor import StrategyAdvisor, AdvisorSuggestion
from engine.intelligence.anomaly_detector import AnomalyDetector

__all__ = [
    "ResearchAgent", "ResearchReport",
    "ModelExplainer", "FeatureImportance",
    "StrategyAdvisor", "AdvisorSuggestion",
    "AnomalyDetector",
]
