from __future__ import annotations

import httpx

from app.adapters.places.base import PlacesAdapter
from app.schemas import PlaceItem, PlacesAlongRouteRequest, PlacesAlongRouteResponse


class GooglePlacesAdapter(PlacesAdapter):
    """Places adapter using Google Places API."""

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
        """Call Google Places API (stubbed until integration)."""
        if not self._api_key:
            return self._fallback(payload)

        # TODO: Implement call to Places API once corridor search is wired.
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
