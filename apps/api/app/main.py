from fastapi import FastAPI

from app.config import get_settings
from app.routers import ai, plans, places, routes

app = FastAPI()


@app.get("/healthz", tags=["monitoring"])
async def healthz() -> dict[str, bool]:
    """Simple health check endpoint."""
    return {"ok": True}


@app.on_event("startup")
async def on_startup() -> None:
    """Load settings and prepare application state."""
    app.state.settings = get_settings()
    app.state.redis = None
    app.state.db_pool = None


app.include_router(routes.router)
app.include_router(places.router)
app.include_router(ai.router)
app.include_router(plans.router)
