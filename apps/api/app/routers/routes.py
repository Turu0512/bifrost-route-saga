from fastapi import APIRouter, status

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/compute", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def compute_route() -> dict[str, str]:
    """Placeholder for route computation."""
    return {"detail": "Not implemented yet"}
