from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import PlacesAlongRouteRequest, PlacesAlongRouteResponse


class PlacesAdapter(ABC):
    """Abstract base class for places search providers."""

    @abstractmethod
    async def search_along_route(
        self, payload: PlacesAlongRouteRequest
    ) -> PlacesAlongRouteResponse:
        """Return places within a corridor around a polyline."""
        raise NotImplementedError
