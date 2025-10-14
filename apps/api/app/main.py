from fastapi import FastAPI

from app.routers import ai, plans, places, routes

app = FastAPI()


@app.get("/healthz", tags=["monitoring"])
async def healthz() -> dict[str, bool]:
    """Simple health check endpoint."""
    return {"ok": True}


app.include_router(routes.router)
app.include_router(places.router)
app.include_router(ai.router)
app.include_router(plans.router)
