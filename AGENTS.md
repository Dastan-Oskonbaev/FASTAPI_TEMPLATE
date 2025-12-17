# Repository Guidelines

## Project Structure & Module Organization
- `src/`: FastAPI application package (entrypoint: `src/main.py`).
- `src/core/`: app setup (`create_app`), configuration (`src/core/config.py`), shared errors/routers.
- Feature modules live under `src/<feature>/` (e.g., `src/auth/`, `src/profile/`, `src/company/`) and typically include:
  - `router.py` (FastAPI routes), `service.py` (business logic), `models.py` (SQLAlchemy), `schemas.py` (Pydantic).
- `src/database/`: SQLAlchemy base/repository; Alembic lives in `src/database/alembic/` (migrations: `src/database/alembic/versions/`).
- `infra/`: environment and deployment files (`infra/envs/`, swarm stacks in `infra/swarm/`).
- `FastAPITemplate.postman_collection.json`: example API requests for local testing.

## Build, Test, and Development Commands
- Install deps (Python 3.12): `poetry install`
- Run locally: `poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
- Run API + Postgres via Docker: `docker compose up -d --build`
- Lint/format:
  - `ruff check .` (CI runs this on merge requests)
  - `ruff format .`
- Migrations:
  - Create: `alembic revision --autogenerate -m "describe change"`
  - Apply: `alembic upgrade head`

## Coding Style & Naming Conventions
- 4-space indentation; line length ≤ 120 (see `pyproject.toml`).
- Prefer type hints; keep routers thin and push logic into `service.py`.
- Naming: modules/files `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- When adding endpoints, wire routers through `src/core/routers.py` so they’re included under the API prefix.

## Testing Guidelines
- Framework: `pytest` (dev dependency). If `tests/` doesn’t exist yet, create it.
- Conventions: `tests/test_*.py`, keep tests deterministic, and cover new routes/services.
- Run: `pytest` (or `poetry run pytest`).

## Commit & Pull Request Guidelines
- Git history is minimal (single initial commit); use clear, imperative messages. Recommended: Conventional Commits (`feat(profile): ...`, `fix(auth): ...`).
- Merge requests should include: summary + rationale, steps to verify locally, any new/changed env vars, and Alembic migrations for schema changes.
- Update the Postman collection when API contracts change.

## Configuration & Security Tips
- Do not commit secrets. Local config is loaded from `infra/envs/.env` (ignored by Git).
- For Docker Compose, `DATABASE_URL` should use the service hostname `db` (example in `README.md`).
