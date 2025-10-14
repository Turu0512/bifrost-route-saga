from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz", tags=["monitoring"])
async def healthz() -> dict[str, bool]:
    """Simple health check endpoint."""
    return {"ok": True}
