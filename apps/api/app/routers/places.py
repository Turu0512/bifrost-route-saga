import hashlib
import json

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.adapters.places import PlacesAdapter
from app.dependencies import get_places_adapter, get_redis
from app.schemas import PlacesAlongRouteRequest, PlacesAlongRouteResponse

router = APIRouter(prefix="/places", tags=["places"])

PLACES_CACHE_TTL = 300  # seconds


@router.post("/along-route", response_model=PlacesAlongRouteResponse)
async def places_along_route(
    payload: PlacesAlongRouteRequest,
    adapter: PlacesAdapter = Depends(get_places_adapter),
    redis_client: Redis | None = Depends(get_redis),
) -> PlacesAlongRouteResponse:
    """Search places along a route corridor using the configured adapter."""
    cache_key = _places_cache_key(payload)
    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return PlacesAlongRouteResponse.model_validate_json(cached)

    response = await adapter.search_along_route(payload)

    if redis_client:
        await redis_client.setex(
            cache_key,
            PLACES_CACHE_TTL,
            response.model_dump_json(),
        )

    return response


def _places_cache_key(payload: PlacesAlongRouteRequest) -> str:
    serialized = json.dumps(payload.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"places:along-route:{digest}"
