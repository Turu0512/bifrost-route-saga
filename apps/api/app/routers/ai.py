from fastapi import APIRouter, Depends

from app.adapters.llm import LLMAdapter
from app.dependencies import get_llm_adapter
from app.schemas import AIPlanRequest, AIPlanResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/plan", response_model=AIPlanResponse)
async def generate_plan(
    payload: AIPlanRequest,
    adapter: LLMAdapter = Depends(get_llm_adapter),
) -> AIPlanResponse:
    """Generate a plan via the configured LLM adapter."""
    return await adapter.generate_plan(payload)
