# Task 1: Project setup: Docker Compose, environment config, and local services

**Status:** pending
**Priority:** high
**Dependencies:** None

## Description
Bootstrap the entire local development environment so all subsequent tasks have working infrastructure to build against.

## Implementation Details
1. Ensure `.env` exists (copy from `.env.example`) and fill in DATABASE_URL, REDIS_URL, OLLAMA_BASE_URL
2. Verify `docker-compose.yml` defines all 4 services: postgres (port 5432), redis (port 6379), api (port 8000), pipeline worker
3. Run `docker compose up postgres redis` to start infrastructure services only
4. Confirm PostgreSQL is reachable: `psql postgresql://lcps:lcps_dev@localhost:5432/lcps_analyzer -c 'SELECT 1'`
5. Confirm Redis is reachable: `redis-cli ping`
6. Pull Gemma 4 model: `ollama pull gemma4:4b` and verify with `ollama list`
7. Create Python virtual environment in `backend/`: `python -m venv .venv && source .venv/bin/activate`
8. Install backend dependencies: `pip install -r requirements.txt`
9. Verify FastAPI starts: `uvicorn app.main:app --reload` shows no import errors

## Test Strategy
All 3 services (postgres, redis, ollama) respond to health checks. FastAPI starts without errors and GET / returns JSON. `ollama list` shows gemma4:4b.
