# FastAPI Template

This is a FastAPI template project designed to quickly set up a new FastAPI-based backend application. It includes configurations for Docker, Docker Compose, and Poetry for dependency management. This template also provides an implementation of JWT authorization, Alembic for database migrations, SQLAlchemy for ORM, and example models to help you get started with your application development.

# Features
- **JWT Authorization**: Secure user authentication using JSON Web Tokens.
- **Alembic for Migrations**: Database migrations and schema management with Alembic.
- **SQLAlchemy ORM**: Object-relational mapping for interacting with the database.
- **Example Models**: Predefined models for common use cases.
- **Example Postman Collections**: Predefined collections for current template.
- **Structured Logging**: JSON logs + request UUID propagation via headers.

# Requirements
- Python 3.12
- Docker (for running via Docker)
- Docker Compose (for running via Docker)

# Clone the repository
```bash
git clone git@gitlab.kg:backend-global/fastapi-template.git
```

# Navigate to the project directory
```bash
cd fastapi-template
```

# Set environment variables
```bash
cp env_example .env
```

Open file and add as basic configuration
```
SECRET_KEY=
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
```

# Start the Docker Compose services in detached mode
```bash
docker compose up -d
```

# Linter check
To run the linter check, use the following command:
```bash
ruff check .
```

# Logging
HTTP requests are logged as JSON lines and include request correlation IDs.

Headers (propagated in both directions):
- `X-Request-UUID` (per request, generated if missing)
- `X-Server-UUID` (per server, generated if missing; can be disabled)

Env vars:
- `SERVICE_NAME` (e.g. `WEB`, `SCHEDULER`, `WORKER`)
- `ENABLE_REQUEST_UUID`, `ENABLE_SERVER_UUID`
- `REQUEST_UUID_HEADER`, `SERVER_UUID_HEADER`
- `UUID_SERVER`, `GENERATE_UUID_SERVER`
- `LOG_REQUEST_BODY`, `LOG_REQUEST_BODY_MAX_BYTES`

# Background
Run ARQ worker and scheduler:
```bash
SERVICE_NAME=WORKER poetry run arq src.background.worker.WorkerSettings
SERVICE_NAME=SCHEDULER poetry run arq src.background.scheduler.SchedulerWorkerSettings
```

# Postman Collection
```plaintext
FastAPITemplate.postman_collection.json
```

# Dump data for database
Make migrations and apply them in docker db container

```bash
docker exec -it fastapi-template-web su
alembic revision --autogenerate -m 'Database init'
alembic upgrade head
```

To make dump data follow these commands.
Data for profiles contains password "secret" to use for login request

```bash
docker exec -it fastapi-template-db su
psql -U postgres -d postgres
INSERT INTO profile (id, login, password, user_type, phone_number, first_name, last_name, middle_name, email, gender, created_date, date_of_birth, updated_date, is_active) VALUES
(1, 'user1', '$2b$12$adf9foG8MZ6JLQxYNgN6c.syHi6n4h5A52qNculjQB3NnR/8m3Z2O', 'admin', '1234567890', 'John', 'Doe', 'M', 'john.doe@example.com', true, '2023-01-01 10:00:00', '1990-01-01', '2023-01-01 10:00:00', true),
(2, 'user2', '$2b$12$adf9foG8MZ6JLQxYNgN6c.syHi6n4h5A52qNculjQB3NnR/8m3Z2O', 'user', '0987654321', 'Jane', 'Smith', 'A', 'jane.smith@example.com', false, '2023-01-02 11:00:00', '1985-05-05', '2023-01-02 11:00:00', true);
```
