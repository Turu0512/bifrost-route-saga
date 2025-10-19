from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import RoutesComputeRequest, RoutesComputeResponse


class RoutesAdapter(ABC):
    """Abstract base class for route computation providers."""

    @abstractmethod
    async def compute_route(self, payload: RoutesComputeRequest) -> RoutesComputeResponse:
        """Compute a primary route and alternatives."""
        raise NotImplementedError
