from __future__ import annotations

import httpx

from typing import Iterable, List, Tuple

import httpx

from app.adapters.places.base import PlacesAdapter
from app.schemas import PlaceItem, PlacesAlongRouteRequest, PlacesAlongRouteResponse


class GooglePlacesAdapter(PlacesAdapter):
    """Places adapter using Google Places API."""

    _SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"
    _FIELD_MASK = (
        "places.id,"
        "places.displayName,"
        "places.location,"
        "places.rating,"
        "places.currentOpeningHours.openNow,"
        "places.shortFormattedAddress"
    )

    def __init__(
        self,
        *,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self._api_key = api_key
        self._client = client

    async def search_along_route(
        self, payload: PlacesAlongRouteRequest
    ) -> PlacesAlongRouteResponse:
        """Call Google Places API to find places along the route."""
        if not self._api_key:
            return self._fallback(payload)

        try:
            center = self._polyline_center(payload.polyline)
        except ValueError:
            return self._fallback(payload)

        radius = payload.corridor_width_m or 3000
        radius = max(500, min(radius, 5000))
        included_types = payload.categories or ["tourist_attraction"]

        request_body: dict[str, object] = {
            "includedTypes": included_types,
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": center[0], "longitude": center[1]},
                    "radius": radius,
                }
            },
        }
        if payload.open_now is not None:
            request_body["openNow"] = payload.open_now

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": self._FIELD_MASK,
        }

        try:
            response = await self._client.post(
                self._SEARCH_URL,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_response(data)
        except (httpx.HTTPError, KeyError, ValueError):
            return self._fallback(payload)

    def _fallback(
        self, payload: PlacesAlongRouteRequest
    ) -> PlacesAlongRouteResponse:
        items = [
            PlaceItem(
                id="p1",
                name="桜島 展望所",
                lat=31.593,
                lng=130.657,
                rating=4.7,
                summary="桜島を望む展望ポイント",
            ),
            PlaceItem(
                id="p2",
                name="指宿温泉 砂むし会館",
                lat=31.234,
                lng=130.642,
                rating=4.5,
                open_now=True,
                summary="名物の砂むし温泉を体験",
            ),
        ]
        return PlacesAlongRouteResponse(items=items)

    def _parse_response(self, data: dict[str, object]) -> PlacesAlongRouteResponse:
        places = data.get("places", [])
        results: List[PlaceItem] = []

        for place in places or []:
            if not isinstance(place, dict):
                continue
            place_id = place.get("id")
            display_name = (
                place.get("displayName", {}).get("text") if isinstance(place.get("displayName"), dict) else None
            )
            location = place.get("location") or {}
            lat = location.get("latitude")
            lng = location.get("longitude")

            if not (place_id and display_name and lat is not None and lng is not None):
                continue

            rating = place.get("rating")
            if isinstance(rating, str):
                try:
                    rating = float(rating)
                except ValueError:
                    rating = None

            open_now = None
            opening_hours = place.get("currentOpeningHours")
            if isinstance(opening_hours, dict):
                open_now = opening_hours.get("openNow")

            summary = place.get("shortFormattedAddress")

            results.append(
                PlaceItem(
                    id=place_id,
                    name=display_name,
                    lat=float(lat),
                    lng=float(lng),
                    rating=float(rating) if rating is not None else None,
                    open_now=open_now,
                    summary=summary,
                )
            )

        if not results:
            raise ValueError("No places parsed")

        return PlacesAlongRouteResponse(items=results)

    @staticmethod
    def _polyline_center(polyline: str) -> Tuple[float, float]:
        points = list(GooglePlacesAdapter._decode_polyline(polyline))
        if not points:
            raise ValueError("Empty polyline")
        lat_sum = sum(lat for lat, _ in points)
        lng_sum = sum(lng for _, lng in points)
        count = len(points)
        return lat_sum / count, lng_sum / count

    @staticmethod
    def _decode_polyline(polyline: str) -> Iterable[Tuple[float, float]]:
        index = lat = lng = 0
        coordinates: List[Tuple[float, float]] = []

        length = len(polyline)
        while index < length:
            shift = result = 0
            while True:
                if index >= length:
                    raise ValueError("Invalid polyline encoding")
                b = ord(polyline[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta_lat = ~(result >> 1) if result & 1 else result >> 1
            lat += delta_lat

            shift = result = 0
            while True:
                if index >= length:
                    raise ValueError("Invalid polyline encoding")
                b = ord(polyline[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta_lng = ~(result >> 1) if result & 1 else result >> 1
            lng += delta_lng

            coordinates.append((lat / 1e5, lng / 1e5))

        return coordinates
