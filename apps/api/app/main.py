from __future__ import annotations

import asyncpg
import httpx
from fastapi import FastAPI
from redis.asyncio import Redis

from app.adapters.llm import GPTOssAdapter, LLMAdapter
from app.adapters.places import GooglePlacesAdapter, PlacesAdapter
from app.adapters.routes import GoogleRoutesAdapter, RoutesAdapter
from app.config import get_settings
from app.repositories.plans import InMemoryPlanRepository, PlanRepository, init_plan_schema
from app.routers import ai, plans, places, routes

app = FastAPI()


@app.get("/healthz", tags=["monitoring"])
async def healthz() -> dict[str, bool]:
    """Simple health check endpoint."""
    return {"ok": True}


@app.on_event("startup")
async def on_startup() -> None:
    """Load settings and prepare application state."""
    settings = get_settings()
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0))
    if settings.testing:
        routes_adapter: RoutesAdapter = GoogleRoutesAdapter(
            api_key="",
            client=http_client,
        )
        places_adapter: PlacesAdapter = GooglePlacesAdapter(
            api_key="",
            client=http_client,
        )
        llm_adapter: LLMAdapter = GPTOssAdapter(
            base_url="",
            api_key=None,
            client=http_client,
        )
        app.state.settings = settings
        app.state.http_client = http_client
        app.state.redis = None
        app.state.db_pool = None
        app.state.routes_adapter = routes_adapter
        app.state.places_adapter = places_adapter
        app.state.llm_adapter = llm_adapter
        app.state.plan_repository = InMemoryPlanRepository()
        return

    redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    db_pool = await asyncpg.create_pool(dsn=settings.database_url)
    await init_plan_schema(db_pool)

    routes_adapter: RoutesAdapter = GoogleRoutesAdapter(
        api_key=settings.google_routes_api_key,
        client=http_client,
    )

    places_adapter: PlacesAdapter = GooglePlacesAdapter(
        api_key=settings.google_places_api_key,
        client=http_client,
    )

    llm_base_url = settings.gpt_oss_base_url or ""
    llm_api_key = settings.gpt_oss_api_key or settings.openai_api_key or ""
    llm_adapter: LLMAdapter = GPTOssAdapter(
        base_url=llm_base_url,
        api_key=llm_api_key,
        client=http_client,
    )

    app.state.settings = settings
    app.state.http_client = http_client
    app.state.redis = redis_client
    app.state.db_pool = db_pool
    app.state.routes_adapter = routes_adapter
    app.state.places_adapter = places_adapter
    app.state.llm_adapter = llm_adapter
    app.state.plan_repository = PlanRepository(db_pool)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Clean up shared resources."""
    client: httpx.AsyncClient | None = getattr(app.state, "http_client", None)
    if client and not client.is_closed:
        await client.aclose()

    settings = getattr(app.state, "settings", None)
    if settings and getattr(settings, "testing", False):
        return

    redis_client: Redis | None = getattr(app.state, "redis", None)
    if redis_client:
        await redis_client.aclose()

    pool: asyncpg.Pool | None = getattr(app.state, "db_pool", None)
    if pool:
        await pool.close()


app.include_router(routes.router)
app.include_router(places.router)
app.include_router(ai.router)
app.include_router(plans.router)
