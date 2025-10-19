from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import AIPlanRequest, AIPlanResponse


class LLMAdapter(ABC):
    """Abstract base class for LLM-backed planners."""

    @abstractmethod
    async def generate_plan(self, payload: AIPlanRequest) -> AIPlanResponse:
        """Generate an itinerary response."""
        raise NotImplementedError
