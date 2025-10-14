from fastapi import APIRouter, status

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_plan() -> dict[str, str]:
    """Placeholder for plan creation."""
    return {"detail": "Not implemented yet"}


@router.get("/{plan_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_plan(plan_id: str) -> dict[str, str]:
    """Placeholder for plan retrieval."""
    return {"detail": f"Not implemented yet for plan_id={plan_id}"}
