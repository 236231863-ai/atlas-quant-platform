"""Experiment API endpoints."""
from __future__ import annotations
from fastapi import APIRouter
router = APIRouter(tags=["experiments"])
@router.get("/experiments/history")
async def experiment_history():
    return {"experiments": [], "total": 0, "note": "Experiment tracking coming soon"}
