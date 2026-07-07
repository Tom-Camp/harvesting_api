# 🌱 🍅 🫛 harvesting.food 🥒 🫐 🥦

An AI-powered garden management API. Users build a personal garden by adding plants, and Google Gemini provides tailored
advice on planting, care, and harvesting based on the user's location.

## Tech Stack

- **Python 3.14** — managed with [uv](https://docs.astral.sh/uv/)
- **FastAPI** — async web framework
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **PostgreSQL** — database
- **Alembic** — migrations
- **Pydantic AI + Anthropic Claude** — AI tips
- **structlog** — structured logging

## Getting Started

### Prerequisites

- Docker (for Postgres)
- Python 3.14
- uv

### 1. Clone and install

```shell
git clone <repo>
cd harvest.food
uv sync
```

### 2. Configure environment

Copy the example and fill in your values:

```shell
cp .env.example .env
```

### 3. Start Postgres

```shell
docker compose up -d
```

### 4. Run migrations

```shell
uv run alembic upgrade head
```

### 5. Start the server

```shell
uv run uvicorn app.main:app --reload
```

API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## User Workflows

### 1. Create an account

```
POST /api/v1/users
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

Location can be as specific or general as the user prefers — city, ZIP code, region, etc. It is used to personalize AI
tips.

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

Plants are the core of the garden. Add plants to your garden and get AI advice on how to grow them. Plants
are categorized by type, which gives a general idea of their growth habits and care needs. The `plant_type` and
`species` fields are required, while `variety` is optional but help provide more specific advice.

#### Plant categories

| Category type | Main examples              | Typical lifespan            |
|---------------|----------------------------|-----------------------------|
| Herb          | Basil, thyme, mint         | Annual or perennial         |
| Vegetable     | Tomato, lettuce, carrot    | Mostly annuals              |
| Fruit         | Strawberry, apple, grape   | Mostly perennials/trees     |
| Flower        | Rose, tulip, zinnia        | Annuals or perennials       |
| Shrub         | Blueberry, hydrangea	Woody | perennial                   |
| Tree          | Apple, maple               | Long‑lived woody perennial  |
| Vine/climber  | Pole bean, cucumber, grape | Annuals or perennials       |

#### Add a plant

```
POST /api/v1/garden/plants
```

```json
{
  "plant_type": "vegetable",
  "species": "tomato",
  "variety": "roma",
  "notes": "Started from seed",
  "planted_date": "2026-04-01T00:00:00Z"
}
```

#### Add a note to a plant

```
POST /api/v1/garden/plants/{plant_id}/notes
```

```json
{ "content": "First true leaves appeared!" }
```

#### View, update, delete plants

```
GET    /api/v1/garden/plants
GET    /api/v1/garden/plants/{plant_id}
PATCH  /api/v1/garden/plants/{plant_id}
DELETE /api/v1/garden/plants/{plant_id}
```

---

### 6. Get AI care information

Request gardening advice for any plant in your garden. The `mode` query parameter selects the type of advice.

```
POST /api/v1/garden/plants/{plant_id}/care
```

The request body includes planting, care, harvesting information and any additional context needed for to raise the
plants.


Response:

```json
{
  "planting": "Plant in early spring after the last frost. Space plants 24-36 inches apart in full sun.",
  "care": "Water deeply once a week, more often in hot weather. Fertilize every 4-6 weeks with a balanced fertilizer. Watch for pests like aphids and tomato hornworms.",
  "harvesting": "Harvest when fruits are fully red and slightly soft to the touch, usually 60-85 days after planting.",
  "latin_name": "Solanum lycopersicum var. roma",
  "summary": "Roma tomatoes thrive in Austin's long growing season. Plant after mid-March and expect fruit by June."
}
```

---

## Development

### Code quality

Pre-commit hooks run automatically on `git commit`. Install them once:

```shell
uv run pre-commit install
```

Run manually against all files:

```shell
uv run pre-commit run --all-files
```

### Tests

```shell
uv run pytest
```

### Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Use `cz commit` for an interactive
prompt:

```shell
uv run cz commit
```

### Migrations

```shell
# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one revision
uv run alembic downgrade -1
```
