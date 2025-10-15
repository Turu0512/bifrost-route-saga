from fastapi import APIRouter

from app.schemas import PlaceItem, PlacesAlongRouteRequest, PlacesAlongRouteResponse

router = APIRouter(prefix="/places", tags=["places"])


@router.post("/along-route", response_model=PlacesAlongRouteResponse)
async def places_along_route(
    payload: PlacesAlongRouteRequest,
) -> PlacesAlongRouteResponse:
    """Temporary stub for places along route lookup."""
    sample_items = [
        PlaceItem(
            id="p1",
            name="桜島 展望所",
            lat=31.593,
            lng=130.657,
            rating=4.7,
            summary="桜島を望む展望ポイント",
        ),
        PlaceItem(
            id="p2",
            name="指宿温泉 砂むし会館",
            lat=31.234,
            lng=130.642,
            rating=4.5,
            open_now=True,
            summary="名物の砂むし温泉を体験",
        ),
    ]
    return PlacesAlongRouteResponse(items=sample_items)
