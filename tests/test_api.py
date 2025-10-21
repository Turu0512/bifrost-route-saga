import pytest


@pytest.mark.asyncio
async def test_healthz(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_create_and_get_plan(client):
    create_payload = {
        "origin": "鹿児島中央駅",
        "destination": "枕崎駅",
        "route_label": "海沿い",
    }

    create_response = await client.post("/plans", json=create_payload)
    assert create_response.status_code == 201
    plan_body = create_response.json()
    assert plan_body["origin"] == create_payload["origin"]
    assert "id" in plan_body

    plan_id = plan_body["id"]
    get_response = await client.get(f"/plans/{plan_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == plan_id
    assert fetched["destination"] == create_payload["destination"]


@pytest.mark.asyncio
async def test_routes_compute(client):
    payload = {
        "origin": "鹿児島中央駅",
        "destination": "枕崎駅",
        "preferScenic": True,
    }
    response = await client.post("/routes/compute", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "polyline" in body
    assert isinstance(body.get("alternatives"), list)
    assert body["alternatives"], "Alternatives should not be empty"


@pytest.mark.asyncio
async def test_places_along_route(client):
    payload = {
        "polyline": "}_ilF~kbkV??",
        "categories": ["tourist_attraction"],
        "corridor_width_m": 1000,
    }
    response = await client.post("/places/along-route", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert isinstance(body["items"], list)
    assert body["items"], "Expected at least one place item"


@pytest.mark.asyncio
async def test_ai_plan(client):
    payload = {
        "origin": "鹿児島中央駅",
        "destination": "枕崎駅",
        "date": "2024-05-01",
    }
    response = await client.post("/ai/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "plan" in body
    assert body["plan"]["origin"] == payload["origin"]
