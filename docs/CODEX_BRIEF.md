````md
# CODEX_BRIEF — route-alchemist

This document is a **concise, machine-friendly brief for code generation**.
Do not over-engineer. Follow the contract below exactly.

## 0) Project Goal

Build a backend **BFF/API** for an AI-assisted scenic drive planner that sits on top of **Google Maps Platform**:

- Compute routes (with alternatives).
- Search POIs along a route corridor.
- Generate a light **AI itinerary** (JSON schema output).
- Save & fetch plans.
  UI is out of scope for now (will be added later).

## 1) Scope (MVP)

Implement the following HTTP endpoints (FastAPI, Python 3.11):

1. `POST /routes/compute`
   - Input: origin, destination, waypoints[], avoidTolls?, trafficAware?, preferScenic?
   - Output: polyline (encoded), distance_m, duration_s, alternatives[] (minimal route cards)
2. `POST /places/along-route`
   - Input: polyline, categories[], corridor_width_m?, open_now?
   - Output: items[] (minimal POI items: id, name, lat, lng, rating?, open_now?, summary?)
3. `POST /ai/plan`
   - Input: origin, destination, date?, preferences{}, candidates{pois[], routes[]}
   - Output: **JSON schema** as defined in `/packages/shared/schemas/ai_plan_output.schema.json`
4. `POST /plans` / `GET /plans/{id}`
   - Create & fetch a plan using `/packages/shared/schemas/plan.schema.json`

> **Authoritative contract:** `openapi.yaml` at repo root.  
> If any discrepancy occurs, **openapi.yaml takes precedence**.

## 2) Non-Goals (MVP)

- No UI. No auth. No payments.
- No long-term caching of Places photos/reviews (respect Google TOS).
- No full turn-by-turn navigation.
- No Mapbox/Valhalla integration yet (leave adapter hooks).

## 3) Tech Stack

- **FastAPI** + **Uvicorn**
- **HTTPX** for outbound calls
- **Redis** (short cache; safe keys only)
- **PostgreSQL** (plans; minimal use in MVP)
- Python typing with **Pydantic v2**
- Docker / Docker Compose

## 4) Environment / Secrets

Use `.env` (already scaffolded):

- `GOOGLE_ROUTES_API_KEY`
- `GOOGLE_PLACES_API_KEY`
- `OPENAI_API_KEY` or `GOOGLE_AI_API_KEY`
- `LLM_PROVIDER` = `openai` | `google`
- `REDIS_URL`
- `DATABASE_URL`

Do **not** expose Google API keys to clients. All calls go through the BFF.

> **Current quarter note:** AI inference will be proxied through a desktop-hosted GPT-OSS instance. Expose it on the internal network and configure the app (`LLM_PROVIDER`, base URL, credentials) so the backend talks to that service instead of cloud-hosted APIs.

## 5) Data Contracts (simplified)

Refer to full JSON Schemas in:

- `/packages/shared/schemas/plan.schema.json`
- `/packages/shared/schemas/ai_plan_output.schema.json`

### 5.1 Request/Response (must match `openapi.yaml`)

**POST /routes/compute (request)**

```json
{
  "origin": "鹿児島中央駅",
  "destination": "枕崎駅",
  "waypoints": ["指宿"],
  "avoidTolls": false,
  "trafficAware": true,
  "preferScenic": true
}
```
````

**POST /routes/compute (response)**

```json
{
  "polyline": "ENCODED_POLYLINE",
  "distance_m": 86000,
  "duration_s": 5520,
  "alternatives": [
    {
      "label": "最短",
      "duration_s": 5520,
      "distance_m": 86000,
      "scenic_score": 42,
      "toll": true
    },
    {
      "label": "海沿い",
      "duration_s": 6480,
      "distance_m": 94000,
      "scenic_score": 88,
      "toll": false
    }
  ]
}
```

**POST /places/along-route (request)**

```json
{
  "polyline": "ENCODED_POLYLINE",
  "categories": ["tourist_attraction", "cafe"],
  "corridor_width_m": 3000,
  "open_now": false
}
```

**POST /places/along-route (response)**

```json
{
  "items": [
    {
      "place_id": "p1",
      "name": "桜島 展望所",
      "lat": 31.593,
      "lng": 130.657,
      "rating": 4.7,
      "open_now": true,
      "summary": "桜島の展望スポット"
    }
  ]
}
```

**POST /ai/plan (request)**

```json
{
  "origin": "鹿児島中央駅",
  "destination": "枕崎駅",
  "preferences": {
    "theme": "coastal",
    "max_distance_km": 150,
    "time_budget_min": 420,
    "avoid_tolls": false
  },
  "candidates": {
    "routes": [
      {
        "label": "最短",
        "duration_s": 5520,
        "distance_m": 86000,
        "scenic_score": 42,
        "toll": true
      },
      {
        "label": "海沿い",
        "duration_s": 6480,
        "distance_m": 94000,
        "scenic_score": 88,
        "toll": false
      }
    ],
    "pois": [
      {
        "place_id": "p1",
        "name": "桜島 展望所",
        "lat": 31.593,
        "lng": 130.657,
        "rating": 4.7,
        "summary": "桜島の展望スポット"
      }
    ]
  }
}
```

**POST /ai/plan (response)**
→ Must conform to `/packages/shared/schemas/ai_plan_output.schema.json`.

**Plan schema** → `/packages/shared/schemas/plan.schema.json`.

## 6) External Calls (outline)

- Google **Routes API** (`computeRoutes`) for route & alternatives.
- Google **Places API** (search along route/corridor).
- LLM provider (OpenAI or Google) for `/ai/plan` with **strict JSON schema output**.

> Implement service code with easy-to-swap adapters:
>
> - `adapters/routes/google_routes.py`
> - `adapters/places/google_places.py`
> - `adapters/llm/openai_llm.py` and `adapters/llm/google_llm.py`

## 7) Caching & Compliance

- Cache hot results in Redis with short TTL (minutes).
- Do not store Places photos/reviews long-term. Save only minimal fields needed.
- Log outbound call latency and response codes.

## 8) Directory Expectations

Code will live under:

```
apps/api/app/
  adapters/        # Google Routes/Places, LLM providers
  routers/         # routes.py, places.py, ai.py, plans.py
  schemas.py
  config.py
```

Shared schemas:

```
packages/shared/schemas/
  plan.schema.json
  ai_plan_output.schema.json
```

Top-level:

```
openapi.yaml
docker-compose.yml
.env.example
```

## 9) Acceptance Criteria

- `docker compose up --build` brings up `api`, `redis`, `db`.
- `GET /healthz` → `{"ok": true}` (200).
- `POST /routes/compute` returns a valid object matching OpenAPI.
- `POST /places/along-route` returns valid minimal POIs.
- `POST /ai/plan` returns JSON conforming to schema (stub acceptable initially).
- `POST /plans` then `GET /plans/{id}` round-trips a plan.

## 10) Implementation Notes

- Keep functions small and testable.
- Use Pydantic models from `schemas.py` for IO.
- Add minimal unit tests for `/healthz` and one endpoint.
- Do not invent fields not present in `openapi.yaml`.

## 11) Future Hooks (comment-only)

- Valhalla/Mapbox adapters for scenic-weighted routing.
- Plan sharing links/QR.
- Auth (user plans).
- Web/Flutter clients consuming this BFF.

```

---

### 補足
- 置き場所は **`docs/CODEX_BRIEF.md`** です（簡潔・機械可読）。
- ここに書いてある **Scope / Contract / Acceptance** を満たすコード生成を促します。
- 仕様の詳細は `openapi.yaml` と `/packages/shared/schemas/*.json` を参照する形にしています。
::contentReference[oaicite:0]{index=0}
```
