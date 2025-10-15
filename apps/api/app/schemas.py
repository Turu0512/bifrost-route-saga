from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RouteComputeWaypoint(BaseModel):
    name: str


class RouteAlternative(BaseModel):
    label: str
    duration_s: int
    distance_m: int
    scenic_score: int
    toll: bool


class RoutesComputeRequest(BaseModel):
    origin: str
    destination: str
    waypoints: list[str] = Field(default_factory=list)
    avoidTolls: bool | None = None
    trafficAware: bool | None = None
    preferScenic: bool | None = None


class RoutesComputeResponse(BaseModel):
    polyline: str
    distance_m: int
    duration_s: int
    alternatives: list[RouteAlternative] = Field(default_factory=list)


class PlacesAlongRouteRequest(BaseModel):
    polyline: str
    categories: list[str] = Field(default_factory=list)
    corridor_width_m: int | None = None
    open_now: bool | None = None


class PlaceItem(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    rating: float | None = None
    open_now: bool | None = None
    summary: str | None = None


class PlacesAlongRouteResponse(BaseModel):
    items: list[PlaceItem] = Field(default_factory=list)


class PlanSegment(BaseModel):
    start_time: str
    end_time: str
    title: str
    description: str | None = None
    poi: PlaceItem | None = None
    travel_mode: Literal["drive", "walk", "stop"] | None = None


class PlanDay(BaseModel):
    date: str
    summary: str | None = None
    segments: list[PlanSegment] = Field(default_factory=list)


class Plan(BaseModel):
    id: UUID | None = None
    origin: str
    destination: str
    route_label: str | None = None
    days: list[PlanDay] = Field(default_factory=list)


class PlanCreateRequest(BaseModel):
    origin: str
    destination: str
    route_label: str | None = None
    days: list[PlanDay] = Field(default_factory=list)


class PlanResponse(Plan):
    pass


class AIPlanPreferences(BaseModel):
    theme: str | None = None
    max_distance_km: int | None = None
    time_budget_min: int | None = None
    avoid_tolls: bool | None = None


class AIPlanCandidates(BaseModel):
    routes: list[RouteAlternative] = Field(default_factory=list)
    pois: list[PlaceItem] = Field(default_factory=list)


class AIPlanRequest(BaseModel):
    origin: str
    destination: str
    date: str | None = None
    preferences: AIPlanPreferences | None = None
    candidates: AIPlanCandidates | None = None


class AIPlanResponse(BaseModel):
    plan: Plan
