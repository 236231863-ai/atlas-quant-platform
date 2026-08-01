import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class CalibrationResult:
    brier_score: float; calibration_error: float; confidence_adjustment: float
    calibration_points: List[Dict[str, float]]; is_well_calibrated: bool; overconfidence: float
    def to_dict(self):
        return asdict(self)

class CalibrationEngine:
    @staticmethod
    def compute_calibration(predicted: List[float], actual: List[int], n_bins: int = 10) -> CalibrationResult:
        if len(predicted) != len(actual): raise ValueError("Length mismatch")
        if not predicted:
            return CalibrationResult(0,0,0,[],True,0)
        brier = sum((p-a)**2 for p,a in zip(predicted,actual))/len(predicted)
        edges = [i/n_bins for i in range(n_bins+1)]
        cpts, ce, bc = [], 0.0, 0
        for i in range(n_bins):
            bp, ba = [], []
            for p, a in zip(predicted, actual):
                if edges[i] <= p < edges[i+1] or (i == n_bins-1 and p == 1.0):
                    bp.append(p); ba.append(a)
            if bp:
                ap = sum(bp)/len(bp); af = sum(ba)/len(ba)
                ce += abs(ap-af); bc += 1
                cpts.append({"bin_center":round((edges[i]+edges[i+1])/2,3),"avg_predicted":round(ap,4),
                    "actual_frequency":round(af,4),"error":round(abs(ap-af),4),"count":len(bp)})
        ce = round(ce/bc,4) if bc>0 else 0.0
        ap2 = sum(predicted)/len(predicted); ar = sum(actual)/len(actual); oc = round(ap2-ar,4)
        adj = round(-oc*0.5,4) if abs(oc) > 0.05 else 0.0
        return CalibrationResult(brier_score=round(brier,6),calibration_error=ce,
            confidence_adjustment=adj,calibration_points=cpts,
            is_well_calibrated=(ce<0.1 and abs(oc)<0.05),overconfidence=oc)

    @staticmethod
    def adjust_probability(probability: float, calibration: CalibrationResult) -> float:
        return max(0.0, min(1.0, probability + calibration.confidence_adjustment))
