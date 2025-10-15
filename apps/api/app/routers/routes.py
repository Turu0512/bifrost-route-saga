from fastapi import APIRouter

from app.schemas import RoutesComputeRequest, RoutesComputeResponse, RouteAlternative

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/compute", response_model=RoutesComputeResponse)
async def compute_route(payload: RoutesComputeRequest) -> RoutesComputeResponse:
    """Temporary stub for route computation."""
    base_alternative = RouteAlternative(
        label="最短",
        duration_s=5400,
        distance_m=84000,
        scenic_score=45,
        toll=True,
    )
    scenic = RouteAlternative(
        label="海沿い",
        duration_s=6300,
        distance_m=91000,
        scenic_score=88,
        toll=False,
    )
    return RoutesComputeResponse(
        polyline="ENCODED_POLYLINE",
        distance_m=base_alternative.distance_m,
        duration_s=base_alternative.duration_s,
        alternatives=[base_alternative, scenic],
    )
