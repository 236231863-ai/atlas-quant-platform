"""Strategy API endpoints."""
from __future__ import annotations
from fastapi import APIRouter
router = APIRouter(tags=["strategies"])
@router.get("/strategies/ranking")
async def strategy_ranking():
    return {"strategies_compared": 0, "ranking": [], "note": "Run a backtest first"}
