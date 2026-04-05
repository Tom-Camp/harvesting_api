# harvesting.food

An AI-powered garden management API. Users build a personal garden by adding plants, and Google Gemini provides tailored advice on planting, care, and harvesting based on the user's location.

## Tech Stack

- **Python 3.14** — managed with [uv](https://docs.astral.sh/uv/)
- **FastAPI** — async web framework
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **PostgreSQL** — database
- **Alembic** — migrations
- **Pydantic AI + Google Gemini** — AI tips
- **Google OIDC** — authentication
- **structlog** — structured logging

## Getting Started

### Prerequisites

- Docker (for Postgres)
- Python 3.14
- uv

### 1. Clone and install

```bash
git clone <repo>
cd harvest.food
uv sync
```

### 2. Configure environment

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```ini
# Postgres
POSTGRES_USER=harvest
POSTGRES_PASSWORD=harvest
POSTGRES_DB=harvest_food
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Google OAuth — https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# JWT — generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=your_jwt_secret

# Pydantic AI — https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key

# App
APP_BASE_URL=http://localhost:8000
LOG_LEVEL=INFO
JSON_LOGS=false
```

### 3. Start Postgres

```bash
docker compose up -d
```

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run uvicorn app.main:app --reload
```

API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## User Workflows

### 1. Sign in with Google

```
GET /api/v1/auth/google/login
```

Returns an `authorization_url`. Redirect the user there. Google authenticates and redirects back to:

```
GET /api/v1/auth/google/callback?code=...&state=...
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "profile_complete": false
}
```

All subsequent requests require the header:

```
Authorization: Bearer <access_token>
```

---

### 2. Complete your profile

New accounts have `profile_complete: false`. Garden and plant endpoints return `403` until location is set.

```
PATCH /api/v1/users/me
```

```json
{ "location": "Austin, TX" }
```

Location can be as specific or general as the user prefers — city, ZIP code, region, etc. It is used to personalise AI tips.

---

### 3. View your profile

```
GET /api/v1/users/me
```

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "picture": "https://...",
  "location": "Austin, TX",
  "created_at": "2026-04-04T12:00:00Z"
}
```

---

### 4. Create your garden

Each user has one garden.

```
POST /api/v1/garden
```

```json
{ "name": "Backyard Garden" }
```

```
GET  /api/v1/garden
PATCH /api/v1/garden   { "name": "Front Yard" }
```

---

### 5. Manage plants

Add plants by type, with an optional variety.

```
POST /api/v1/garden/plants
```

```json
{ "plant_type": "tomato", "variety": "roma", "notes": "Started from seed" }
```

```
GET    /api/v1/garden/plants
GET    /api/v1/garden/plants/{plant_id}
PATCH  /api/v1/garden/plants/{plant_id}   { "notes": "Transplanted outdoors" }
DELETE /api/v1/garden/plants/{plant_id}
```

---

### 6. Get AI tips

Request gardening advice for any plant in your garden. The `mode` query parameter selects the type of advice.

```
POST /api/v1/garden/plants/{plant_id}/tips?mode=planting
POST /api/v1/garden/plants/{plant_id}/tips?mode=care
POST /api/v1/garden/plants/{plant_id}/tips?mode=harvest
```

| Mode | Description |
|---|---|
| `planting` | When and how to plant based on your location and climate |
| `care` | Watering, fertilising, and troubleshooting common problems |
| `harvest` | Signs of ripeness and how to harvest |

Response:

```json
{
  "mode": "planting",
  "plant_type": "tomato",
  "variety": "roma",
  "location": "Austin, TX",
  "tips": [
    { "title": "Best Planting Time", "content": "In Austin, TX, start roma tomatoes outdoors after the last frost, typically mid-March..." },
    { "title": "Soil Preparation", "content": "Roma tomatoes prefer well-drained soil with a pH of 6.0–6.8..." }
  ],
  "summary": "Roma tomatoes thrive in Austin's long growing season. Plant after mid-March and expect fruit by June."
}
```

---

## Development

### Code quality

Pre-commit hooks run automatically on `git commit`. Install them once:

```bash
uv run pre-commit install
```

Run manually against all files:

```bash
uv run pre-commit run --all-files
```

### Tests

```bash
uv run pytest
```

### Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Use `cz commit` for an interactive prompt:

```bash
uv run cz commit
```

### Migrations

```bash
# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one revision
uv run alembic downgrade -1
```
