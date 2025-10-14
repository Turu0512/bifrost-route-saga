from fastapi import APIRouter, status

router = APIRouter(prefix="/places", tags=["places"])


@router.post("/along-route", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def places_along_route() -> dict[str, str]:
    """Placeholder for places along route lookup."""
    return {"detail": "Not implemented yet"}
