<p align="center">
  <img src="docs/imgs/subsurface_data_platform_banner.svg" alt="Subsurface Data Platform banner" width="100%" />
</p>

# Subsurface Data Platform

A cloud-oriented, multi-user platform for managing and analyzing subsurface data (well logs and seismic data), built around role-based access control instead of hardcoded UI permissions.

## ⚠️ Development Status

This project is in an **early stage of development**. What exists today is a **work-in-progress MVP**, not a finished or production-ready system.

Concretely, as of now:

- The **backend** has an application skeleton (FastAPI) plus a working JWT authentication/authorization flow (registration, login, access/refresh tokens, role model, automated tests) backed by a relational database via SQLAlchemy/Alembic.
- The **frontend** (Vue 3 + Vite) and **API Gateway** (Node.js) are directory scaffolds only — no application logic yet.
- **Cloud infrastructure** (Lambda, API Gateway, S3, DynamoDB, RDS, Terraform) described in this README is the **intended architecture**, not something already deployed or provisioned.
- LAS/SEG-Y upload, processing, and petrophysical calculations are **planned features**, not implemented.

Sections below distinguish **current implementation**, **planned features**, and **project goals** wherever that distinction matters. Treat anything not explicitly marked as implemented as a design intention.

## Overview

Subsurface Data Platform aims to be a cloud-oriented, multi-user platform for uploading, visualizing, and analyzing subsurface data — well logs (LAS) and seismic data (SEG-Y) — with access control enforced by role rather than by what a UI happens to show.

The project intentionally combines three disciplines:

- **Software engineering** — a typed FastAPI backend, service-layer architecture, JWT-based auth, automated tests.
- **Geoscience domain modeling** — LAS/SEG-Y file handling and petrophysical calculations, scoped to a small, well-defined MVP.
- **Cloud engineering** — an AWS-based architecture (Lambda, API Gateway, S3, DynamoDB, RDS) provisioned with Terraform.

## Key Features

**Implemented today:**

- JWT-based authentication (access + refresh tokens).
- User registration and login backed by a PostgreSQL-compatible database (via SQLAlchemy, async).
- Password hashing (Argon2), no plaintext or reversible password storage.
- A `UserRole` domain model (`Geologist`, `Reservoir Engineer`, `Admin`) used to scope authorization.
- A protected endpoint (`/api/users/me`) demonstrating token-based authorization.
- Automated tests covering registration, login, token validation, and access control.

**Planned:**

- LAS and SEG-Y file upload and storage.
- Basic subsurface data visualization.
- Petrophysical calculations restricted to the Reservoir Engineer role.
- User and role management restricted to Administrators.
- Deployment as containerized Lambda functions behind API Gateway with a Lambda Authorizer.

## User Roles / RBAC

The platform is designed around three fixed roles:

- **Geologist**
  - Upload LAS and SEG-Y files.
  - Visualize subsurface data.
  - Cannot delete data.

- **Reservoir Engineer**
  - Visualize data.
  - Perform basic petrophysical calculations.
  - Export results.

- **Administrator**
  - Manage users and roles.
  - Full access to the platform.

Authorization is intended to be enforced **server-side**, via JWT claims and role checks in the API layer — not by hiding buttons in the frontend. The current backend already models roles on the `User` entity and encodes them in issued tokens; role-scoped endpoint restrictions (e.g. delete permissions, admin-only routes) are part of the MVP scope described below and are being built out incrementally.

## Architecture

Target architecture (see [Development Status](#️-development-status) for what is actually running today):

```text
Vue.js Frontend
       │
     HTTPS
       ▼
API Gateway
       │
Lambda Authorizer
(JWT + RBAC)
       │
       ▼
Lambda / FastAPI Backend
       │
       ├── S3
       │   └── Raw LAS / SEG-Y
       │
       ├── DynamoDB
       │   └── Metadata
       │
       └── RDS / PostgreSQL
           └── Users and Roles

S3 upload
    │
    ▼
Lambda container
    │
    ▼
LAS / SEG-Y processing
```

**Component responsibilities:**

- **Vue.js Frontend** — user interface for upload, visualization, and calculations; talks to the backend only through the API Gateway over HTTPS.
- **API Gateway** — single entry point for all client requests; routes traffic to the backend and applies the Lambda Authorizer before requests reach application code.
- **Lambda Authorizer (JWT + RBAC)** — validates the JWT on each request and enforces role-based access before invoking the backend, so authorization is centralized rather than duplicated per endpoint.
- **Lambda / FastAPI Backend** — the application itself (this repository's `backend/`), packaged to run either as a conventional service or as a container-based Lambda function.
- **S3** — stores raw LAS/SEG-Y files as uploaded, unmodified.
- **DynamoDB** — stores file and dataset metadata (e.g. upload info, processing status).
- **RDS / PostgreSQL** — stores users, roles, and relational application data; this is what the current backend already connects to via SQLAlchemy/Alembic.
- **Processing pipeline** — an S3 upload event triggers a Lambda container that parses and processes LAS/SEG-Y files asynchronously from the request/response cycle.

## Technology Stack

| Area | Technology | Status |
|---|---|---|
| Frontend | Vue 3 + Vite | Scaffold only |
| API Gateway service | Node.js | Scaffold only |
| Backend | FastAPI (Python 3.11+) | Implemented (auth flow) |
| Backend auth | JWT (PyJWT), Argon2 password hashing | Implemented |
| Database (relational) | PostgreSQL / Amazon RDS or Aurora Serverless v2 | Implemented locally via SQLAlchemy + Alembic; RDS/Aurora provisioning planned |
| Database (documents) | Amazon DynamoDB | Planned |
| Object storage | Amazon S3 | Planned |
| Compute | AWS Lambda | Planned |
| Edge / routing | Amazon API Gateway | Planned |
| AuthZ at the edge | Lambda Authorizer | Planned |
| IAM | AWS IAM | Planned |
| Infrastructure as code | Terraform | Planned |
| Containerization | Docker | Partial (Dockerfiles exist per service; no orchestrated Compose stack yet) |
| Access control model | RBAC | Implemented in domain model; endpoint-level enforcement in progress |

## MVP Scope

The MVP intentionally targets a small, demonstrable slice of the full architecture:

- Three fixed roles: Geologist, Reservoir Engineer, Administrator.
- Upload of one small LAS file.
- Upload of one small SEG-Y file.
- One simple petrophysical calculation, restricted to the Reservoir Engineer role.
- A basic user management interface, restricted to Administrators.
- **Authorization tests**, including a test proving that a Geologist receives `403 Forbidden` when attempting to delete data.

Authorization testing is a deliberate focus of this project: it demonstrates that RBAC is enforced by the backend itself, not only by what the frontend chooses to display. The existing test suite (`backend/tests/`) already follows this principle for authentication (e.g. rejecting invalid/expired/malformed tokens, rejecting an access token where a refresh token is required) and will be extended with role-based authorization cases as those endpoints are implemented.

## Out of Scope

The MVP explicitly does **not** include:

- Multi-tenancy / multiple organizations.
- Dynamic role creation.
- Advanced seismic processing.
- Seismic inversion.
- Complex seismic attributes.
- Notifications.
- Full audit logging.
- Advanced observability beyond basic CloudWatch logging.
- Production continuous deployment.

At this stage, CI is expected to demonstrate automated tests and `terraform plan` only — not automated deployment.

## Project Structure

```text
/
├── backend/          # FastAPI application (implemented: auth flow, scaffolded: rest)
│   ├── app/
│   │   ├── api/          # routers, dependencies, exception handlers
│   │   ├── core/         # db session/base, security (JWT, hashing), logging
│   │   ├── domain/       # enums (roles) and domain exceptions
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # business logic / use cases
│   │   ├── settings.py
│   │   └── main.py
│   ├── alembic/          # database migrations
│   ├── tests/
│   └── pyproject.toml
├── api-gateway/       # Node.js service (scaffold only)
├── frontend/          # Vue 3 + Vite application (scaffold only)
├── docs/              # project documentation and assets
├── docker-compose.yml # currently minimal; per-service orchestration not yet defined
├── .dockerignore
└── .gitignore
```

## Local Development

> The steps below cover what is currently runnable — the backend. Frontend and API Gateway are scaffolds without application behavior yet.

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -e ".[dev]"

cp .env.example .env
# edit .env with local values (database URL, JWT secret, etc.)

uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Environment Variables

Defined in `backend/app/settings.py` and documented in `backend/.env.example`:

| Variable | Purpose | Example |
|---|---|---|
| `CORS_ORIGINS` | Allowed origins for CORS | `["http://localhost:5173"]` |
| `DATABASE_URL` | Async SQLAlchemy database URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/subsurface` |
| `JWT_SECRET` | Secret used to sign JWTs | *(set per environment, never commit real secrets)* |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRY` | Access token lifetime, in seconds | `3600` |
| `REFRESH_TOKEN_EXPIRY` | Refresh token lifetime, in seconds | `604800` |

## Testing

The backend test suite uses `pytest` with `pytest-asyncio` and an in-memory SQLite database, so it runs without any external services.

```bash
cd backend
pip install -e ".[dev]"
pytest tests/ -v
```

Current coverage includes:

- Registration (success, duplicate email, password never stored in plaintext).
- Login (success, wrong password, unknown email).
- JWT handling (valid access/refresh tokens, expired tokens, malformed tokens).
- The refresh-token endpoint (rejects access tokens, accepts refresh tokens).
- Basic authorization (authenticated vs. unauthenticated access to a protected endpoint).

Role-scoped authorization tests (e.g. the Geologist-cannot-delete case from the MVP scope) will be added alongside the endpoints they protect.

## Infrastructure / Terraform

Infrastructure as code is a planned part of this project and is **not yet implemented in this repository**. The intent is to manage the AWS resources described in [Architecture](#architecture) — API Gateway, Lambda, S3, DynamoDB, RDS/Aurora, IAM — with Terraform, and for CI to run `terraform plan` (not `apply`) at this stage, alongside the automated test suite.

Docker support exists per service (`backend/Dockerfile`, `frontend/Dockerfile`, `api-gateway/Dockerfile`); a shared `docker-compose.yml` is present at the repository root but does not yet define services, as local multi-service orchestration has not been wired up.

## Roadmap

Roughly in order:

1. Implement role-scoped endpoint authorization (delete restrictions, admin-only routes) and the corresponding tests.
2. Implement LAS and SEG-Y upload endpoints and storage.
3. Implement the single petrophysical calculation in MVP scope.
4. Build the minimal Vue 3 frontend for upload, visualization, and the admin user-management view.
5. Introduce Terraform definitions for the target AWS architecture, validated via `terraform plan` in CI.
6. Wire up the API Gateway service and/or Lambda Authorizer, depending on final deployment shape.
7. Expand CI to run backend tests and infrastructure validation on every change.

## License

No license has been chosen for this repository yet. All rights reserved by the author until a license is added.
