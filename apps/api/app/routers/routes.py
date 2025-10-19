from fastapi import APIRouter, Depends

from app.adapters.routes import RoutesAdapter
from app.dependencies import get_routes_adapter
from app.schemas import RoutesComputeRequest, RoutesComputeResponse

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/compute", response_model=RoutesComputeResponse)
async def compute_route(
    payload: RoutesComputeRequest,
    adapter: RoutesAdapter = Depends(get_routes_adapter),
) -> RoutesComputeResponse:
    """Compute a route using the configured adapter."""
    return await adapter.compute_route(payload)
