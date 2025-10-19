from __future__ import annotations

from typing import Any

import httpx

from app.adapters.routes.base import RoutesAdapter
from app.schemas import (
    RouteAlternative,
    RoutesComputeRequest,
    RoutesComputeResponse,
)


class GoogleRoutesAdapter(RoutesAdapter):
    """Routes adapter using Google Routes API."""

    def __init__(
        self,
        *,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self._api_key = api_key
        self._client = client

    async def compute_route(
        self, payload: RoutesComputeRequest
    ) -> RoutesComputeResponse:
        """Call Google Routes API (stubbed until integration)."""
        if not self._api_key:
            return self._fallback(payload)

        # TODO: Replace with real Google Routes API call.
        return self._fallback(payload)

    def _fallback(self, payload: RoutesComputeRequest) -> RoutesComputeResponse:
        primary = RouteAlternative(
            label="最短",
            duration_s=5520,
            distance_m=86000,
            scenic_score=42,
            toll=True,
        )
        scenic = RouteAlternative(
            label="海沿い",
            duration_s=6480,
            distance_m=94000,
            scenic_score=88,
            toll=False,
        )
        return RoutesComputeResponse(
            polyline="ENCODED_POLYLINE",
            distance_m=primary.distance_m,
            duration_s=primary.duration_s,
            alternatives=[primary, scenic],
        )
