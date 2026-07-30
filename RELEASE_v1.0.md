# Atlas Quant Platform v1.0.0 - Release Documentation

## Overview

Atlas Quant Platform v1.0.0 is a production-ready quantitative research platform.
Built across 8 sprints with clean architecture, domain-driven design, and engine-first philosophy.

## System Architecture

```
UI Layer (Web Dashboard + Desktop Client)
    |
API Layer (FastAPI REST endpoints)
    |
Service Layer (Business orchestration)
    |
Engine Layer (Pure computation: analysis, backtest, strategy, simulation, statistics, optimization)
    |
Data Layer (SQLAlchemy ORM + Repositories)
    |
Database (SQLite dev / PostgreSQL prod)
```

## Components

| Component | Technology | Location |
|-----------|-----------|----------|
| Backend API | Python 3.11, FastAPI, SQLAlchemy 2.x | backend/ |
| Web Dashboard | React, TypeScript, Vite, ECharts | frontend/ |
| Desktop Client | PySide6, matplotlib | desktop/ |
| Computation Engine | NumPy, Pandas, SciPy, StatsModels | engine/ |
| AI Integration | OpenAI compatible adapters | core/ai/ |
| Database | SQLite (dev) / PostgreSQL 15 (prod) | — |
| Containerization | Docker + Docker Compose | docker/ |

## API Endpoints

health - GET /health
draws - GET/POST /api/v1/{lottery}/draws, /latest, /statistics
dashboard - GET /api/v1/dashboard/summary
strategies - GET /api/v1/strategies/ranking
experiments - GET /api/v1/experiments/history
research - GET /api/v1/research/reports
users - CRUD /api/v1/users, /workspaces, /projects

## Quick Start

```bash
# Production
docker-compose -f docker/docker-compose.yml up -d

# Development
poetry install --all-groups
make db-migrate
uvicorn backend.api.v1.app:app --reload
```

## Configuration

Environment variables via .env or system env:
- ATLAS_ENVIRONMENT (development/production)
- ATLAS_DB__URL (database connection)
- ATLAS_LOG__LEVEL (logging level)
- ATLAS_AI__OPENAI_API_KEY (OpenAI API key)

## Testing

Total project tests: 700+
Run: pytest --cov=core --cov=engine --cov=backend

## License

MIT License
