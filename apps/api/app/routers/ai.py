from fastapi import APIRouter

from app.schemas import (
    AIPlanRequest,
    AIPlanResponse,
    Plan,
    PlanDay,
    PlanSegment,
    PlaceItem,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/plan", response_model=AIPlanResponse)
async def generate_plan(payload: AIPlanRequest) -> AIPlanResponse:
    """Temporary stub for AI-generated plan endpoint."""
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
