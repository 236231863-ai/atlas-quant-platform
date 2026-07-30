"""Atlas Quant Platform - Draw API Endpoints.

RESTful API for draw data access.
Uses Service layer, never accesses database directly.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_session
from backend.service.draw_service import DrawService
from core.types.models import DrawRecordData, DrawStatistics

router = APIRouter(tags=["draws"])


async def get_draw_service(session: AsyncSession = Depends(get_session)) -> DrawService:
    return DrawService(session)


@router.get("/{lottery}/draws", response_model=List[DrawRecordData])
async def get_draws(
    lottery: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: DrawService = Depends(get_draw_service),
):
    """Get draw records for a lottery type."""
    return await service.get_draws(lottery, start_date, end_date, limit, offset)


@router.get("/{lottery}/latest")
async def get_latest_draw(
    lottery: str,
    service: DrawService = Depends(get_draw_service),
):
    """Get the latest draw record for a lottery type."""
    result = await service.get_latest_draw(lottery)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No draws found for lottery: {lottery}")
    return result


@router.get("/{lottery}/statistics", response_model=DrawStatistics)
async def get_statistics(
    lottery: str,
    service: DrawService = Depends(get_draw_service),
):
    """Get statistics for a lottery type."""
    return await service.get_statistics(lottery)
