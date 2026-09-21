# BenchFlow

BenchFlow is a **pet project** for managing test benches and controlling concurrent run starts.

The project focuses on backend engineering: API design, authentication and authorization,
transactional persistence, clean architecture, concurrency control, migrations, and automated tests.
It is not intended to replace CI/CD systems such as Jenkins or full-featured laboratory management platforms.

## Features

- FastAPI REST API
- PostgreSQL persistence with SQLAlchemy 2.0
- Alembic migrations
- JWT access-token authentication
- role-based access control with `USER` and `ADMIN` roles
- bench CRUD operations
- run start workflow with `AVAILABLE -> BUSY` transition
- Redis-backed distributed lock for concurrent run starts
- Repository and Unit of Work abstractions
- unit, integration, API, migration, smoke, and concurrency tests
- CI with pytest, Ruff, and mypy

## Domain model

### User

A user can have one of two roles:

- `USER` — can authenticate and start runs
- `ADMIN` — can additionally create, update, and delete benches

New registrations always receive the `USER` role.

### Bench

A bench can be in one of the following states:

- `available`
- `busy`
- `maintenance`
- `offline`

### Run

The run model defines three states:

- `running`
- `completed`
- `failed`

The current version implements run admission only.
Starting a run creates a `RUNNING` run and changes the bench from `AVAILABLE` to `BUSY`.

## Architecture

The project follows a layered Clean Architecture-style structure:

```text
benchflow/
├── domain/
│   ├── bench.py              # Bench entity and status
│   ├── run.py                # Run entity and status
│   └── user.py               # User entity and roles
│
├── application/
│   ├── ports/                # Repository, Unit of Work and lock interfaces
│   └── services/             # Authentication, bench and run use cases
│
├── infrastructure/
│   ├── db/
│   │   ├── models/           # SQLAlchemy persistence models
│   │   ├── repositories/     # PostgreSQL repository implementations
│   │   ├── session.py        # Async SQLAlchemy session setup
│   │   └── unit_of_work.py   # SQLAlchemy Unit of Work
│   ├── redis/                # Redis-backed bench locking
│   └── security/             # JWT and password hashing implementations
│
└── presentation/
    ├── routes/               # FastAPI endpoints
    ├── schemas/              # Request/response models
    ├── dependencies/         # Authentication, authorization and DI
    └── lifespan.py           # Application resource lifecycle
```

## Authentication and authorization

Authentication uses short-lived JWT access tokens; refresh tokens are not implemented yet.

User roles are loaded from PostgreSQL on authenticated requests rather than stored in the token.
Public registration always creates a `USER`; `ADMIN` accounts are currently assigned manually.

Administrators can manage benches, while authenticated users can start runs.
The full API contract is available through FastAPI's OpenAPI documentation.

## Concurrency control

Concurrent run starts are protected by a Redis-backed lock using `SET NX EX`.
PostgreSQL remains the source of truth for bench and run state.

For the current single-database topology, Redis is arguably unnecessary:
PostgreSQL row locking or an atomic conditional update would likely be simpler.

Redis becomes more useful when the critical section extends beyond a single database transaction,
for example when the backend accepts a run request and a worker on another machine spends tens of seconds
preparing a physical bench and then runs a long test.

## Running locally

### Requirements

- Python 3.12+
- Docker
- Docker Compose

### 1. Install the project

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Replace `JWT_SECRET` in `.env` with your own secret of at least 32 characters.

### 3. Start PostgreSQL and Redis

```bash
docker compose up -d postgres redis
```

Docker Compose provides local PostgreSQL and Redis infrastructure.
The FastAPI application itself runs locally.

### 4. Apply migrations

```bash
alembic upgrade head
```

### 5. Start the API

```bash
uvicorn benchflow.main:app --reload
```

Interactive OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

There is no frontend in the current version; the API is intended to be explored through OpenAPI documentation or another
HTTP client.

## Tests and quality checks

Run the complete test suite:

```bash
pytest
```

Run static checks:

```bash
ruff check .
mypy benchflow tests
```

Integration tests use disposable PostgreSQL and Redis containers through Testcontainers,
so Docker must be available when running the full suite.

GitHub Actions runs the same checks for pushes and pull requests to `dev` and `main`.

## Scope and trade-offs

The current scope is intentionally limited:

- run completion and external test execution are not implemented yet
- the Redis lock uses a fixed TTL without lease renewal or fencing
- the Unit of Work is intentionally explicit to make transaction boundaries and persistence isolation visible

## Why this project exists

BenchFlow was built to explore backend engineering beyond simple CRUD:
layered architecture, explicit transaction boundaries, authentication and RBAC,
migrations, concurrency control, and integration testing against real infrastructure.