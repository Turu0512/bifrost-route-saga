from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from app.adapters.routes.base import RoutesAdapter
from app.schemas import (
    RouteAlternative,
    RoutesComputeRequest,
    RoutesComputeResponse,
)


class GoogleRoutesAdapter(RoutesAdapter):
    """Routes adapter using Google Routes API."""

    _API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
    _FIELD_MASK = (
        "routes.duration,"
        "routes.distanceMeters,"
        "routes.polyline.encodedPolyline,"
        "routes.travelAdvisory.tollInfo,"
        "routes.routeLabels"
    )

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
        """Call Google Routes API to compute the route."""
        if not self._api_key:
            return self._fallback(payload)

        request_body = self._build_request_body(payload)
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": self._FIELD_MASK,
        }

        try:
            response = await self._client.post(
                self._API_URL,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            payload_data = response.json()
            return self._parse_response(payload, payload_data)
        except (httpx.HTTPError, ValidationError, KeyError, ValueError):
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

    def _build_request_body(self, payload: RoutesComputeRequest) -> dict[str, Any]:
        body: dict[str, Any] = {
            "origin": {"address": payload.origin},
            "destination": {"address": payload.destination},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL"
            if payload.trafficAware
            else "TRAFFIC_AWARE",
            "computeAlternativeRoutes": True,
            "routeModifiers": {},
        }

        if payload.waypoints:
            body["intermediates"] = [{"address": wp} for wp in payload.waypoints]

        modifiers = body["routeModifiers"]
        if payload.avoidTolls is not None:
            modifiers["avoidTolls"] = payload.avoidTolls

        # Prefer scenic has no direct toggle; hint via route objective when set.
        if payload.preferScenic:
            body["optimizeWaypointOrder"] = True

        if not modifiers:
            body.pop("routeModifiers")

        return body

    def _parse_response(
        self, payload: RoutesComputeRequest, data: dict[str, Any]
    ) -> RoutesComputeResponse:
        routes = data.get("routes", [])
        if not routes:
            raise ValueError("Empty routes response")

        primary_route = routes[0]
        polyline = (
            primary_route.get("polyline", {}).get("encodedPolyline") or "ENCODED_POLYLINE"
        )
        distance = primary_route.get("distanceMeters", 0)
        duration = self._duration_to_seconds(primary_route.get("duration", "0s"))

        alternatives: list[RouteAlternative] = []
        for index, route in enumerate(routes):
            label = self._label_for_route(index)
            toll_info = route.get("travelAdvisory", {}).get("tollInfo")
            scenic_score = self._estimate_scenic_score(index, payload.preferScenic)
            duration_seconds = self._duration_to_seconds(route.get("duration", "0s"))
            distance_meters = route.get("distanceMeters", 0)

            alternatives.append(
                RouteAlternative(
                    label=label,
                    duration_s=duration_seconds,
                    distance_m=distance_meters,
                    scenic_score=scenic_score,
                    toll=bool(toll_info),
                )
            )

        return RoutesComputeResponse(
            polyline=polyline,
            distance_m=distance,
            duration_s=duration,
            alternatives=alternatives,
        )

    @staticmethod
    def _duration_to_seconds(duration: str) -> int:
        if not duration:
            return 0
        if duration.endswith("s"):
            try:
                return int(float(duration.rstrip("s")))
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _label_for_route(index: int) -> str:
        if index == 0:
            return "最短"
        return f"代替{index}"

    @staticmethod
    def _estimate_scenic_score(index: int, prefer_scenic: bool | None) -> int:
        base = 70 if prefer_scenic else 55
        adjustment = max(0, base - index * 10)
        return max(10, min(95, adjustment))
