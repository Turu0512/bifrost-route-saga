from fastapi import APIRouter, status

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/plan", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def generate_plan() -> dict[str, str]:
    """Placeholder for AI-generated plan endpoint."""
    return {"detail": "Not implemented yet"}
