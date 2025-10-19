from fastapi import APIRouter, Depends

from app.adapters.places import PlacesAdapter
from app.dependencies import get_places_adapter
from app.schemas import PlacesAlongRouteRequest, PlacesAlongRouteResponse

router = APIRouter(prefix="/places", tags=["places"])


@router.post("/along-route", response_model=PlacesAlongRouteResponse)
async def places_along_route(
    payload: PlacesAlongRouteRequest,
    adapter: PlacesAdapter = Depends(get_places_adapter),
) -> PlacesAlongRouteResponse:
    """Search places along a route corridor using the configured adapter."""
    return await adapter.search_along_route(payload)
