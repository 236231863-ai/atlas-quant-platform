"""Atlas Quant Platform - FastAPI Application."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.draws import router as draws_router
from backend.api.v1.dashboard import router as dashboard_router
from backend.api.v1.strategies import router as strategies_router
from backend.api.v1.experiments import router as experiments_router
from backend.api.v1.research import router as research_router
from backend.api.v1.users import router as users_router

app = FastAPI(title="Atlas Quant Platform API", version="1.0.0", description="Quantitative research platform API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def add_disclaimer(request, call_next):
    response = await call_next(request)
    response.headers["X-Atlas-Disclaimer"] = "Academic research only. Does not predict lottery outcomes."
    return response

app.include_router(draws_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(strategies_router, prefix="/api/v1")
app.include_router(experiments_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
