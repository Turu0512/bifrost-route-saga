from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_plan_repository
from app.repositories.plans import PlanRepository
from app.schemas import PlanCreateRequest, PlanResponse

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: PlanCreateRequest,
    repository: PlanRepository = Depends(get_plan_repository),
) -> PlanResponse:
    """Persist a plan using the configured repository."""
    return await repository.create_plan(payload)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    repository: PlanRepository = Depends(get_plan_repository),
) -> PlanResponse:
    """Fetch a stored plan."""
    plan = await repository.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan
