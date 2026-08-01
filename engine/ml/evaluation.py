"""Model Evaluation - accuracy, precision, recall, calibration error, overfitting."""
from __future__ import annotations
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.probability.calibration import CalibrationEngine

@dataclass
class EvalMetrics:
    accuracy: float = 0.0; precision: float = 0.0; recall: float = 0.0; f1_score: float = 0.0
    calibration_error: float = 0.0; overfitting_score: float = 0.0; is_overfit: bool = False
    def to_dict(self):
        return asdict(self)

class ModelEvaluation:
    @staticmethod
    def compute_metrics(y_true: List[float], y_pred: List[float]) -> EvalMetrics:
        if not y_true or not y_pred or len(y_true) != len(y_pred):
            return EvalMetrics()
        n = len(y_true)
        correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
        accuracy = correct / n
        tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
        fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
        fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return EvalMetrics(accuracy=round(accuracy,4), precision=round(precision,4),
            recall=round(recall,4), f1_score=round(f1,4))

    @staticmethod
    def compute_calibration_metrics(y_prob: List[float], y_true: List[int]) -> EvalMetrics:
        cal = CalibrationEngine.compute_calibration(y_prob, y_true)
        y_pred = [1 if p >= 0.5 else 0 for p in y_prob]
        base = ModelEvaluation.compute_metrics([float(x) for x in y_true], [float(x) for x in y_pred])
        base.calibration_error = cal.calibration_error; base.is_overfit = False
        return base

    @staticmethod
    def detect_overfitting(train_accuracy: float, test_accuracy: float, threshold: float = 0.15) -> Tuple[float, bool]:
        gap = train_accuracy - test_accuracy
        score = round(gap, 4)
        return (score, gap > threshold)
