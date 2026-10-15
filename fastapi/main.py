import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, HTTPException


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    value = int(raw)
    if value < 1:
        raise RuntimeError(f"{name} must be a positive integer")
    return value


workers = env_int("WEB_CONCURRENCY", 2)
pool_max = env_int("APP_CONCURRENCY", 50)
if pool_max < workers:
    raise RuntimeError("APP_CONCURRENCY must be at least WEB_CONCURRENCY")
pool_size = pool_max // workers


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await asyncpg.create_pool(
        host=os.environ.get("DB_HOST", "postgres"),
        port=env_int("DB_PORT", 5432),
        user=os.environ.get("DB_USERNAME", "rps"),
        password=os.environ.get("DB_PASSWORD", "rps"),
        database=os.environ.get("DB_DATABASE", "rps"),
        min_size=pool_size,
        max_size=pool_size,
        command_timeout=10,
    )
    app.state.pool = pool
    try:
        yield
    finally:
        await pool.close()


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/api/ping")
async def ping():
    try:
        await app.state.pool.fetchval("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Server Error") from exc
    return {"status": "ok"}
