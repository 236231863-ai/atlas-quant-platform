"""Scientific Review Board - peer review committee."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ReviewResult:
    review_id: str; reviewer: str; criteria: str; score: float; comment: str; decision: str = "pending"
    def to_dict(self): return asdict(self)

class ScientificReviewBoard:
    def __init__(self):
        self._reviewers = ["Statistician","Methodologist","RiskReviewer","ReproducibilityReviewer","InnovationReviewer"]
        self._results: List[ReviewResult] = []

    def peer_review(self, research_id: str) -> List[ReviewResult]:
        results = []
        for r in self._reviewers:
            score = 0.5 + (hash(r + research_id) % 50) / 100
            result = ReviewResult(review_id=f"rev_{research_id}_{r}", reviewer=r, criteria="quality",
                score=round(score, 2), comment=f"{r} review completed")
            self._results.append(result); results.append(result)
        return results

    def score_research(self, research_id: str) -> Dict[str, Any]:
        reviews = [r for r in self._results if research_id in r.review_id]
        if not reviews: return {"avg_score": 0, "count": 0}
        scores = [r.score for r in reviews]
        return {"avg_score": round(sum(scores)/len(scores), 2), "count": len(scores),
                "min_score": min(scores), "max_score": max(scores)}

    def approve_publication(self, research_id: str, threshold: float = 0.6) -> bool:
        scores = self.score_research(research_id)
        return scores["avg_score"] >= threshold

    def get_results(self) -> List[ReviewResult]: return self._results
    def count(self) -> int: return len(self._results)
