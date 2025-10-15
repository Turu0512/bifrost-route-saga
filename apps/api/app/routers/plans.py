from __future__ import annotations

from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas import Plan, PlanCreateRequest, PlanResponse, PlanDay

router = APIRouter(prefix="/plans", tags=["plans"])

_FAKE_PLAN_STORE: Dict[UUID, Plan] = {}


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(payload: PlanCreateRequest) -> PlanResponse:
    """Persist a plan in an in-memory store (placeholder until DB wiring)."""
    plan_id = uuid4()
    plan = Plan(
        id=plan_id,
        origin=payload.origin,
        destination=payload.destination,
        route_label=payload.route_label,
        days=payload.days or _default_plan_days(),
    )
    _FAKE_PLAN_STORE[plan_id] = plan
    return PlanResponse(**plan.model_dump())


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: UUID) -> PlanResponse:
    """Retrieve a plan from the in-memory store."""
    plan = _FAKE_PLAN_STORE.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return PlanResponse(**plan.model_dump())


def _default_plan_days() -> list[PlanDay]:
    """Provide a minimal placeholder itinerary when none is supplied."""
    return [
        PlanDay(
            date="2024-01-01",
            summary="サンプル旅程",
            segments=[],
        )
    ]
