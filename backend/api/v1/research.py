"""Research API endpoints."""
from __future__ import annotations
from fastapi import APIRouter
router = APIRouter(tags=["research"])
@router.get("/research/reports")
async def research_reports():
    return {"reports": [], "note": "Research report generation coming soon"}
