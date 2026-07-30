"""Integration tests for expanded FastAPI endpoints."""
from __future__ import annotations
import pytest
from datetime import date
from httpx import AsyncClient, ASGITransport
from backend.api.v1.app import app
from backend.database.session import init_db, create_engine, create_session_factory, get_session
from backend.database.models import LotteryGame, DrawRecord
pytestmark = pytest.mark.integration

@pytest.fixture
async def client():
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    factory = create_session_factory(engine)
    async def override_get_session():
        async with factory() as s: yield s
    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await engine.dispose()
    app.dependency_overrides.clear()

class TestExpandedAPI:
    async def test_health(self, client):
        r = await client.get("/health"); assert r.status_code == 200
        assert r.json()["version"] == "0.7.0"
    async def test_dashboard_summary(self, client):
        r = await client.get("/api/v1/dashboard/summary"); assert r.status_code == 200
        data = r.json(); assert "total_games" in data
    async def test_strategy_ranking(self, client):
        r = await client.get("/api/v1/strategies/ranking"); assert r.status_code == 200
        data = r.json(); assert "strategies_compared" in data
    async def test_experiment_history(self, client):
        r = await client.get("/api/v1/experiments/history"); assert r.status_code == 200
        assert "experiments" in r.json()
    async def test_research_reports(self, client):
        r = await client.get("/api/v1/research/reports"); assert r.status_code == 200
        data = r.json(); assert "reports" in data
    async def test_draws_empty(self, client):
        r = await client.get("/api/v1/dlt/draws"); assert r.status_code == 200
        assert r.json() == []
    async def test_latest_not_found(self, client):
        r = await client.get("/api/v1/dlt/latest"); assert r.status_code == 404
    async def test_statistics_empty(self, client):
        r = await client.get("/api/v1/dlt/statistics"); assert r.status_code == 200
        assert r.json()["lottery_code"] == "dlt"
    async def test_disclaimer_header(self, client):
        r = await client.get("/health"); assert "X-Atlas-Disclaimer" in r.headers
    async def test_dashboard_has_games_list(self, client):
        r = await client.get("/api/v1/dashboard/summary"); d = r.json()
        assert isinstance(d.get("games"), list)
