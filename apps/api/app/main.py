from __future__ import annotations

import httpx
from fastapi import FastAPI

from app.adapters.llm import GPTOssAdapter, LLMAdapter
from app.adapters.places import GooglePlacesAdapter, PlacesAdapter
from app.adapters.routes import GoogleRoutesAdapter, RoutesAdapter
from app.config import get_settings
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
    app.state.redis = None
    app.state.db_pool = None
    app.state.routes_adapter = routes_adapter
    app.state.places_adapter = places_adapter
    app.state.llm_adapter = llm_adapter


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Clean up shared resources."""
    client: httpx.AsyncClient | None = getattr(app.state, "http_client", None)
    if client and not client.is_closed:
        await client.aclose()


app.include_router(routes.router)
app.include_router(places.router)
app.include_router(ai.router)
app.include_router(plans.router)
