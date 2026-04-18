## v1.0.2 (2026-04-18)

### Fix

- **Dockerfile**: fixing perms for docker

## v1.0.1 (2026-04-18)

### Fix

- **Dockerfile**: add user
- **dockerfile**: updating dockerfile and docker-compose

## v1.0.0 (2026-04-18)

### Feat

- **zxcvbn**: adding password complexity
- **email**: adding reset password endpoints
- **Dockerfile**: adding dockerfile and github workflow
- **plant**: adding archive unarchive
- **Plant**: updating plant model to include harvest and not objects
- **Harvest**: add harvest endpoints
- **Harvest**: adding harvest service
- **Harvest**: adding the harvest model
- **Notes**: adding endpoints for note crud
- **Note**: adding label field to note model
- **Plant**: adding plot field to plant model
- **Auth**: adding google auth
- **middleware.py**: adding structlog logging

### Fix

- **garden_advisor.py**: improve the ai prompt
- **api.v1.plants.py**: added CareInfo object creation and association with Plant object
- **Plant**: plant restructure with ai care values and note list
- **base.py**: adding base model with id, created_date, and updated_date fields
- **main.py**: adding lifespan function with db dispose
- **class**: Correcting AI agent and model

### Refactor

- **docker-publish**: fixing image path
- **Plant**: moving latin name from care to Plant model
- **garden_advisor.py**: changing from google gemini to claude haiku
- **plant.py**: updating plant model and schema
- **app**: refactor of app removing google auth
- **slugifying-garden-name**: adding slugify for cleaner paths
