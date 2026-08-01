"""Pattern Mining Engine - discover hidden research patterns."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
import math
from collections import Counter

@dataclass
class ResearchPattern:
    pattern_id: str; description: str; pattern_type: str; impact: str; confidence: float; features: List[str]
    def to_dict(self):
        return asdict(self)

class PatternMiningEngine:
    @staticmethod
    def discover_correlations(feature_matrix: List[Dict[str, float]], target: str = "sharpe_ratio") -> List[Dict[str, Any]]:
        if not feature_matrix or len(feature_matrix) < 3: return []
        targets = [f.get(target, 0) for f in feature_matrix]
        feature_keys = [k for k in feature_matrix[0].keys() if k != target] if feature_matrix else []
        correlations = []
        for key in feature_keys:
            vals = [f.get(key, 0) for f in feature_matrix]
            n = len(vals)
            mean_x, mean_y = sum(vals)/n, sum(targets)/n
            num = sum((vals[i]-mean_x)*(targets[i]-mean_y) for i in range(n))
            den = math.sqrt(sum((vals[i]-mean_x)**2 for i in range(n))) * math.sqrt(sum((targets[i]-mean_y)**2 for i in range(n)))
            r = num/den if den > 0 else 0
            correlations.append({"feature":key,"correlation":round(r,4)})
        return sorted(correlations, key=lambda c: abs(c["correlation"]), reverse=True)

    @staticmethod
    def extract_success_patterns(experiments: List[Dict[str, Any]], threshold: float = 0.5) -> List[ResearchPattern]:
        patterns = []
        for e in experiments:
            m = e.get("metrics", {})
            if m.get("sharpe_ratio",0) >= threshold:
                params = e.get("params", {})
                features = list(params.keys())
                if features:
                    patterns.append(ResearchPattern(pattern_id=f"success_{len(patterns)+1}",
                        description=f"Strategy with {features} achieved Sharpe {m['sharpe_ratio']:.2f}",
                        pattern_type="success", impact="positive", confidence=m.get("sharpe_ratio",0.5),
                        features=features))
        return patterns

    @staticmethod
    def extract_failure_patterns(experiments: List[Dict[str, Any]], threshold: float = -0.3) -> List[ResearchPattern]:
        patterns = []
        for e in experiments:
            m = e.get("metrics", {})
            if m.get("sharpe_ratio",0) <= threshold:
                params = e.get("params", {})
                features = list(params.keys())
                if features:
                    patterns.append(ResearchPattern(pattern_id=f"failure_{len(patterns)+1}",
                        description=f"Strategy with {features} failed (Sharpe {m['sharpe_ratio']:.2f})",
                        pattern_type="failure", impact="negative", confidence=abs(m.get("sharpe_ratio",0)),
                        features=features))
        return patterns
