"""Atlas Quant Platform - Machine Learning Research Layer.

ML is for RESEARCH, not prediction.
Pure computation: no IO, no database.
"""
from __future__ import annotations
from engine.ml.feature_pipeline import FeaturePipeline, FeatureVector
from engine.ml.models import ModelAdapter, RandomForestAdapter, ModelConfig
from engine.ml.evaluation import ModelEvaluation, EvalMetrics
__all__ = ["FeaturePipeline","FeatureVector","ModelAdapter","RandomForestAdapter","ModelConfig","ModelEvaluation","EvalMetrics"]
