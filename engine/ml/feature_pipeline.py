"""Feature Pipeline - connects engine/features/ into FeatureVector."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from core.types.models import DrawRecordData
from engine.features import compute_frequency_features, compute_gap_features, compute_distribution_features, compute_entropy_features, compute_pair_features

@dataclass
class FeatureVector:
    number: int; frequency_rate: float = 0.0; z_score: float = 0.0; current_gap: int = 0
    avg_gap: float = 0.0; gap_ratio: float = 0.0; odd_even_ratio: float = 0.0
    high_low_ratio: float = 0.0; zone_pct: float = 0.0; entropy_score: float = 0.0
    pair_strength: float = 0.0; normalized_entropy: float = 0.0
    def to_vector(self) -> List[float]:
        return [self.frequency_rate, self.z_score, float(self.current_gap), self.avg_gap,
                self.gap_ratio, self.odd_even_ratio, self.high_low_ratio, self.zone_pct,
                self.entropy_score, self.pair_strength, self.normalized_entropy]
    def to_dict(self):
        return asdict(self)
    @property
    def feature_names(self) -> List[str]:
        return ["frequency_rate","z_score","current_gap","avg_gap","gap_ratio",
                "odd_even_ratio","high_low_ratio","zone_pct","entropy_score","pair_strength","normalized_entropy"]

class FeaturePipeline:
    @staticmethod
    def compute_vector(number: int, draws: List[DrawRecordData], main_range: Tuple[int, int]) -> FeatureVector:
        if not draws: return FeatureVector(number=number)
        freq = compute_frequency_features(draws, main_range)
        gap = compute_gap_features(draws, main_range)
        dist = compute_distribution_features(draws, main_range)
        ent = compute_entropy_features(draws, main_range)
        pair = compute_pair_features(draws, main_range)
        sn = str(number)
        return FeatureVector(
            number=number,
            frequency_rate=freq.get("features",{}).get(sn,{}).get("frequency_rate",0),
            z_score=freq.get("features",{}).get(sn,{}).get("z_score",0),
            current_gap=gap.get("features",{}).get(sn,{}).get("current_gap",0),
            avg_gap=gap.get("features",{}).get(sn,{}).get("avg_gap",0),
            gap_ratio=gap.get("features",{}).get(sn,{}).get("gap_ratio",0),
            odd_even_ratio=dist.get("features",{}).get("odd_even_ratio_current",0),
            high_low_ratio=dist.get("features",{}).get("high_low_ratio_current",0),
            zone_pct=dist.get("features",{}).get("zone_low_pct",0),
            entropy_score=ent.get("features",{}).get("shannon_entropy",0),
            normalized_entropy=ent.get("features",{}).get("normalized_entropy",0),
            pair_strength=pair.get("features",{}).get("total_pairs_analyzed",0),
        )

    @staticmethod
    def compute_vectors(numbers: List[int], draws: List[DrawRecordData], main_range: Tuple[int, int]) -> List[FeatureVector]:
        return [FeaturePipeline.compute_vector(n, draws, main_range) for n in numbers]

    @staticmethod
    def to_feature_matrix(vectors: List[FeatureVector]) -> Tuple[List[List[float]], List[int]]:
        X = [v.to_vector() for v in vectors]
        y = [v.number for v in vectors]
        return X, y
