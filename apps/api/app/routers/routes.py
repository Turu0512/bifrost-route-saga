import json
import hashlib

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.adapters.routes import RoutesAdapter
from app.dependencies import get_redis, get_routes_adapter
from app.schemas import RoutesComputeRequest, RoutesComputeResponse

router = APIRouter(prefix="/routes", tags=["routes"])

ROUTE_CACHE_TTL = 300  # seconds


@router.post("/compute", response_model=RoutesComputeResponse)
async def compute_route(
    payload: RoutesComputeRequest,
    adapter: RoutesAdapter = Depends(get_routes_adapter),
    redis_client: Redis | None = Depends(get_redis),
) -> RoutesComputeResponse:
    """Compute a route using the configured adapter."""
    cache_key = _routes_cache_key(payload)
    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return RoutesComputeResponse.model_validate_json(cached)

    response = await adapter.compute_route(payload)

    if redis_client:
        await redis_client.setex(
            cache_key,
            ROUTE_CACHE_TTL,
            response.model_dump_json(),
        )

    return response


def _routes_cache_key(payload: RoutesComputeRequest) -> str:
    serialized = json.dumps(payload.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"routes:compute:{digest}"
