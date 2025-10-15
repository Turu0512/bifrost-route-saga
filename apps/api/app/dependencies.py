"""Application-level dependency helpers.

The actual connection wiring (Redis, PostgreSQL) will be filled in once
the adapters are implemented. For now we expose placeholders so routers
can depend on them without failing.
"""

from typing import AsyncIterator

import asyncpg
from fastapi import Depends, Request
from redis.asyncio import Redis

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
