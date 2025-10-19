from __future__ import annotations

import json
from typing import Any
from uuid import UUID, uuid4

import asyncpg

from app.schemas import Plan, PlanCreateRequest, PlanDay, PlanResponse

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    route_label TEXT,
    plan JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

INSERT_PLAN_SQL = """
INSERT INTO plans (id, origin, destination, route_label, plan)
VALUES ($1, $2, $3, $4, $5)
RETURNING id, plan;
"""

GET_PLAN_SQL = """
SELECT id, plan
FROM plans
WHERE id = $1;
"""


async def init_plan_schema(pool: asyncpg.Pool) -> None:
    """Ensure the plans table exists."""
    async with pool.acquire() as conn:
        await conn.execute(CREATE_TABLE_SQL)


class PlanRepository:
    """Repository handling CRUD for plans."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create_plan(self, payload: PlanCreateRequest) -> PlanResponse:
        plan_id = uuid4()
        plan_model = Plan(
            id=plan_id,
            origin=payload.origin,
            destination=payload.destination,
            route_label=payload.route_label,
            days=payload.days,
        )
        plan_json = json.dumps(plan_model.model_dump(mode="json"))

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                INSERT_PLAN_SQL,
                plan_id,
                plan_model.origin,
                plan_model.destination,
                plan_model.route_label,
                plan_json,
            )

        return self._row_to_plan_response(row)

    async def get_plan(self, plan_id: UUID) -> PlanResponse | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(GET_PLAN_SQL, plan_id)

        if row is None:
            return None
        return self._row_to_plan_response(row)

    def _row_to_plan_response(self, row: asyncpg.Record) -> PlanResponse:
        raw_plan = row["plan"]
        if isinstance(raw_plan, str):
            data: dict[str, Any] = json.loads(raw_plan)
        else:
            data = dict(raw_plan)
        data["id"] = str(row["id"])
        return PlanResponse(**data)


class InMemoryPlanRepository:
    """Simple in-memory repository used for testing."""

    def __init__(self) -> None:
        self._store: dict[UUID, PlanResponse] = {}

    async def create_plan(self, payload: PlanCreateRequest) -> PlanResponse:
        plan_id = uuid4()
        plan = Plan(
            id=plan_id,
            origin=payload.origin,
            destination=payload.destination,
            route_label=payload.route_label,
            days=payload.days or [PlanDay(date="2024-01-01", summary=None, segments=[])],
        )
        response = PlanResponse(**plan.model_dump())
        self._store[plan_id] = response
        return response

    async def get_plan(self, plan_id: UUID) -> PlanResponse | None:
        return self._store.get(plan_id)
