"""Dashboard API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.service.draw_service import DrawService
import random

router = APIRouter(tags=["dashboard"])

async def get_svc(session=Depends(get_session)):
    return DrawService(session)

@router.get("/dashboard/summary")
async def dashboard_summary(svc: DrawService = Depends(get_svc)):
    games = await svc.list_games()
    summary = {"total_games": len(games), "games": []}
    for g in games:
        stats = await svc.get_statistics(g.code)
        summary["games"].append(stats.to_dict())
    return summary
