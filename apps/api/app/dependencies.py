"""Application-level dependency helpers."""

import asyncpg
from fastapi import Request
from redis.asyncio import Redis

from app.adapters.llm import LLMAdapter
from app.adapters.places import PlacesAdapter
from app.adapters.routes import RoutesAdapter
from app.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Resolve application settings."""
    return get_settings()


async def get_redis(request: Request) -> Redis | None:
    """Return the Redis client stored on the application state, if any."""
    return getattr(request.app.state, "redis", None)


async def get_db_pool(request: Request) -> asyncpg.Pool | None:
    """Return the asyncpg pool stored on the application state, if any."""
    return getattr(request.app.state, "db_pool", None)


def get_routes_adapter(request: Request) -> RoutesAdapter:
    """Provide the configured routes adapter."""
    adapter = getattr(request.app.state, "routes_adapter", None)
    if adapter is None:
        raise RuntimeError("Routes adapter is not configured")
    return adapter


def get_places_adapter(request: Request) -> PlacesAdapter:
    """Provide the configured places adapter."""
    adapter = getattr(request.app.state, "places_adapter", None)
    if adapter is None:
        raise RuntimeError("Places adapter is not configured")
    return adapter


def get_llm_adapter(request: Request) -> LLMAdapter:
    """Provide the configured LLM adapter."""
    adapter = getattr(request.app.state, "llm_adapter", None)
    if adapter is None:
        raise RuntimeError("LLM adapter is not configured")
    return adapter
