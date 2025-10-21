from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from app.adapters.llm.base import LLMAdapter
from app.schemas import AIPlanRequest, AIPlanResponse, Plan, PlanDay, PlanSegment, PlaceItem


class GPTOssAdapter(LLMAdapter):
    """Adapter talking to a self-hosted GPT-OSS endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        client: httpx.AsyncClient,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = client

    async def generate_plan(self, payload: AIPlanRequest) -> AIPlanResponse:
        """Call GPT-OSS backend to produce a plan."""
        if not self._base_url:
            return self._fallback(payload)

        url = f"{self._base_url}/v1/plan"
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        request_body: dict[str, Any] = payload.model_dump(mode="json")

        try:
            response = await self._client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()
            return AIPlanResponse.model_validate(data)
        except (httpx.HTTPError, ValidationError, ValueError):
            # TODO: surface an explicit error response once GPT-OSS integration is production ready.
            return self._fallback(payload)

    def _fallback(self, payload: AIPlanRequest) -> AIPlanResponse:
        scenic_stop = PlaceItem(
            id="p1",
            name="長崎鼻灯台",
            lat=31.238,
            lng=130.501,
            summary="開聞岳と東シナ海を望む絶景ポイント",
        )
        day_plan = PlanDay(
            date=payload.date or "2024-01-01",
            summary="海沿いドライブと絶景巡り",
            segments=[
                PlanSegment(
                    start_time="09:00",
                    end_time="10:30",
                    title="鹿児島中央駅を出発",
                    description="レンタカーを借りて枕崎へ向かうドライブ開始。",
                    travel_mode="drive",
                ),
                PlanSegment(
                    start_time="11:00",
                    end_time="12:30",
                    title="長崎鼻灯台でフォトストップ",
                    description="展望台からの眺めを楽しみ、カフェで休憩。",
                    poi=scenic_stop,
                    travel_mode="stop",
                ),
            ],
        )
        plan = Plan(
            origin=payload.origin,
            destination=payload.destination,
            route_label="海沿い",
            days=[day_plan],
        )
        return AIPlanResponse(plan=plan)
