# User Authentication Platform

A monorepo containing a **React 19 single-page frontend** and a **Flask 3 REST API**
backed by **PostgreSQL 16**, orchestrated with **Docker Compose**.

The approved design is documented in [`docs/architecture.md`](docs/architecture.md); the
incremental delivery plan lives in [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md).

> **Status: repository scaffold only.**
> This commit delivers the monorepo skeleton and root configuration. There is no
> application code, no Docker Compose file and no dependency manifests yet - see
> [What is not implemented yet](#what-is-not-implemented-yet).

---

## Table of contents

1. [Project overview](#project-overview)
2. [Technology stack](#technology-stack)
3. [Repository layout](#repository-layout)
4. [Prerequisites](#prerequisites)
5. [Environment configuration](#environment-configuration)
6. [Running the stack (intended)](#running-the-stack-intended)
7. [Local development notes (intended)](#local-development-notes-intended)
8. [What is not implemented yet](#what-is-not-implemented-yet)
9. [Documentation](#documentation)

---

## Project overview

The application lets a visitor browse public pages (Home, About Us, Contact Us),
register an account, log in and reach a protected dashboard.

* The **frontend** is an API-only consumer: a Vite-built React 19 SPA using Material UI
  components with Tailwind CSS utilities for layout, and React Router DOM for client
  routing. The JWT returned by the API is kept in memory and mirrored to
  `localStorage`, then attached as an `Authorization: Bearer <token>` header.
* The **backend** is an API-only Flask application factory exposing versioned endpoints
  under `/api/v1` (`/auth/register`, `/auth/login`, `/auth/me`, `/health`). Passwords are
  hashed with Flask-Bcrypt and tokens issued with Flask-JWT-Extended.
* The **database** is PostgreSQL 16, accessed through SQLAlchemy with schema migrations
  managed by Flask-Migrate (Alembic).

All three run as separate services under Docker Compose (`db`, `backend`, `frontend`).

---

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite 5, Material UI 6 (+ @emotion), Tailwind CSS 3, React Router DOM 7, axios |
| Frontend tests | Vitest + React Testing Library |
| Backend | Python 3.11, Flask 3 (application factory + blueprints), Flask-SQLAlchemy 3 / SQLAlchemy 2, Flask-Migrate 4, Flask-Bcrypt, Flask-JWT-Extended 4, Flask-Cors, email-validator, python-dotenv |
| Backend server | gunicorn (in the container) |
| Backend tests | pytest + pytest-flask |
| Database | PostgreSQL 16 (`psycopg2-binary` driver) |
| Static serving | nginx:alpine (serves the built frontend) |
| Tooling | Docker, Docker Compose |

> Note: although Jinja2/Bootstrap appear in the wider stack catalogue, this project has
> **no server-rendered pages** - the UI is React-only, as stated in the architecture.

---

## Repository layout

```text
.
├── backend/            # Flask API service root            [PLACEHOLDER - no code yet]
│   └── .gitkeep
├── frontend/           # React SPA service root             [PLACEHOLDER - no code yet]
│   └── .gitkeep
├── docs/
│   ├── architecture.md # Approved architecture (source of truth)
│   └── BUILD_PLAN.md   # Phased delivery plan
├── .env.example        # Template for the git-ignored root .env
├── .gitignore
└── Readme.md           # This file
```

The target structure these placeholders will grow into (per the architecture's *Folder
Structure* section) is:

```text
backend/
├── app/
│   ├── __init__.py          # create_app() application factory
│   ├── extensions.py        # db, migrate, bcrypt, jwt, cors singletons
│   ├── config.py            # Development / Production / Testing config classes
│   ├── api/                 # auth.py, health.py blueprints
│   ├── models/              # user.py
│   ├── schemas/             # auth_schemas.py
│   └── utils/               # errors.py, responses.py, validators.py
├── migrations/              # Flask-Migrate (Alembic) output
├── tests/                   # pytest suite
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── wsgi.py

frontend/
├── src/
│   ├── api/                 # client.js, auth.js
│   ├── components/          # Navbar, Layout, forms, ProtectedRoute, Alert
│   ├── context/             # AuthContext.jsx
│   ├── pages/               # Home, About, Contact, Register, Dashboard, NotFound
│   ├── utils/               # validators.js
│   └── tests/               # Vitest specs
├── Dockerfile
├── nginx.conf
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json

docker-compose.yml           # db + backend + frontend services (repo root)
```

---

## Prerequisites

| Tool | Minimum version | Needed for |
| --- | --- | --- |
| Docker Engine | 24+ | Running the full stack |
| Docker Compose | v2 (`docker compose`) | Orchestrating `db`, `backend`, `frontend` |
| Python | 3.11 | Running the backend outside Docker |
| Node.js | 20+ (with npm 10+) | Running the frontend outside Docker |
| Git | any recent | Cloning the repository |

Only Docker and Docker Compose are required for the containerised workflow; Python and
Node are needed for local (non-Docker) development.

---

## Environment configuration

All configuration is supplied through environment variables - **no secrets are committed**.
Copy the template and edit the placeholder values:

```bash
cp .env.example .env
```

Then open `.env` and replace at least `POSTGRES_PASSWORD`, `JWT_SECRET_KEY` and
`SECRET_KEY` with your own values. `.env` is git-ignored; `.env.example` is tracked.

### Variables

| Variable | Group | Purpose | Example placeholder |
| --- | --- | --- | --- |
| `POSTGRES_USER` | Postgres | DB user created by the `db` service | `user` |
| `POSTGRES_PASSWORD` | Postgres | Password for that user | `password` |
| `POSTGRES_DB` | Postgres | Application database name | `dbname` |
| `DATABASE_URL` | Backend | SQLAlchemy connection string (host `db` = Compose service) | `postgresql://user:password@db:5432/dbname` |
| `JWT_SECRET_KEY` | Backend | Signing key for JWT access tokens | `change-me-jwt-secret-key` |
| `SECRET_KEY` | Backend | Flask secret key | `change-me-flask-secret-key` |
| `FRONTEND_ORIGIN` | Backend | CORS-allowed browser origin | `http://localhost:3000` |
| `VITE_API_BASE_URL` | Frontend | API base URL used by axios | `http://localhost:5000/api/v1` |

Keep the values consistent: `DATABASE_URL` must embed the same `POSTGRES_USER`,
`POSTGRES_PASSWORD` and `POSTGRES_DB` values and point at the Compose service host `db`
on port `5432`.

---

## Running the stack (intended)

> ⚠️ `docker-compose.yml` and the service Dockerfiles are **not part of this commit**.
> The commands below are the documented target workflow and will work once the Docker
> task of Phase 1 lands.

```bash
# 1. Configure the environment
cp .env.example .env

# 2. Build and start db + backend + frontend
docker compose up --build

# 3. Apply database migrations (first run / after model changes)
docker compose exec backend flask db upgrade

# 4. Stop the stack (add -v to also drop the pgdata volume)
docker compose down
```

Planned published endpoints:

| Service | URL |
| --- | --- |
| Frontend (nginx) | <http://localhost:3000> |
| Backend API | <http://localhost:5000/api/v1> |
| Health check | <http://localhost:5000/api/v1/health> |
| PostgreSQL | `localhost:5432` (inside the network: host `db`) |

---

## Local development notes (intended)

These steps describe how the services will be run outside Docker once their code and
dependency manifests exist.

### Backend (Python 3.11)

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # file arrives in a later task

# Point DATABASE_URL at localhost instead of the `db` service name when the
# database runs in Docker but the API runs on the host, e.g.
#   postgresql://user:password@localhost:5432/dbname
flask --app wsgi.py db upgrade
flask --app wsgi.py run --debug --port 5000
```

Tests (once present): `pytest` from the `backend/` directory.

### Frontend (Node 20+)

```bash
cd frontend
npm install                      # package.json arrives in a later task
npm run dev                      # Vite dev server on http://localhost:3000
```

Tests (once present): `npm run test` (Vitest + React Testing Library).

---

## What is not implemented yet

This commit contains **documentation and configuration only**. Nothing is runnable yet.

* ❌ `docker-compose.yml` and the `backend/Dockerfile` / `frontend/Dockerfile`.
* ❌ Flask application factory, config classes, extensions, blueprints and error handlers.
* ❌ `backend/requirements.txt`, `backend/wsgi.py`, `backend/pytest.ini`.
* ❌ SQLAlchemy `User` model and Flask-Migrate migrations.
* ❌ Any API endpoint - `/api/v1/health`, `/api/v1/auth/*` do not exist yet.
* ❌ `frontend/package.json`, Vite/Tailwind config and all React source files.
* ❌ Backend (pytest) and frontend (Vitest) test suites.

✅ Delivered here: the `backend/` and `frontend/` tracked placeholders, `docs/architecture.md`,
`docs/BUILD_PLAN.md`, this `Readme.md`, the root `.env.example` and the root `.gitignore`.

---

## Documentation

* [`docs/architecture.md`](docs/architecture.md) - overview, stack, folder structure, data
  model, API conventions, coding standards and shared components. **Single source of
  truth** for folder names, environment variable names, ports and service names.
* [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) - phased implementation plan.
