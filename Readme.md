# Full-Stack Authentication Application

A responsive **React 19 + Vite** single-page frontend (Material UI + Tailwind CSS, React
Router DOM) talking to a **Flask 3** REST API (SQLAlchemy, Flask-Migrate, Flask-Bcrypt,
Flask-JWT-Extended) backed by **PostgreSQL 16**. Every service runs in its own container
and the whole stack is orchestrated with Docker Compose.

---

## Project Structure

```text
project/
  backend/              # Flask API service
    app/                # application package (factory, api, models, utils)
    migrations/         # Flask-Migrate (Alembic) revisions
    tests/              # pytest suite
    Dockerfile
    requirements.txt
    wsgi.py
  frontend/             # React 19 + Vite SPA
    src/                # pages, components, context, api client, utils, tests
    Dockerfile          # multi-stage: node build -> nginx:alpine runtime
    nginx.conf          # static serving + SPA history fallback
    vite.config.js
  docs/                 # architecture documentation
  docker-compose.yml
  .env.example
  Readme.md
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Docker Engine | 24+ |
| Docker Compose | v2 (`docker compose`) |
| Node.js (only for local Vite dev) | 20 LTS |
| Python (only for local backend dev) | 3.11 |

Ports **3000** (frontend), **5000** (backend API) and **5432** (PostgreSQL) must be free,
or overridden in `.env`.

---

## 1. Environment setup

Copy the sample environment file at the repository root and adjust the values
(secrets, ports, credentials):

```bash
cp .env.example .env
```

Key variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | database credentials | `appuser` / `appsecret` / `appdb` |
| `DATABASE_URL` | SQLAlchemy URL used by the backend container | `postgresql+psycopg2://appuser:appsecret@db:5432/appdb` |
| `SECRET_KEY`, `JWT_SECRET_KEY` | Flask / JWT secrets - **change for anything but local dev** | `change-me-*` |
| `FRONTEND_ORIGIN` | CORS origin accepted by the API | `http://localhost:3000` |
| `VITE_API_BASE_URL` | API base URL baked into the SPA at **build** time | `http://localhost:5000/api/v1` |
| `FRONTEND_PORT` / `BACKEND_PORT` | published host ports | `3000` / `5000` |

> `FRONTEND_ORIGIN` must match the URL the browser uses to load the SPA, otherwise the
> browser blocks API calls with a CORS error.

The frontend also ships `frontend/.env.example` for local (non-Docker) development:

```bash
cp frontend/.env.example frontend/.env
```

In the container build the value is **not** read from that file - it is passed as the
`VITE_API_BASE_URL` build argument by Compose, because Vite inlines `VITE_*` variables at
build time.

---

## 2. Run the full stack with Docker Compose

From the repository root:

```bash
docker compose up --build
```

This builds and starts three services:

| Service | Description | URL / Port |
|---------|-------------|------------|
| `db` | PostgreSQL 16 with the named volume `pgdata` and a healthcheck | `localhost:5432` |
| `backend` | Flask API served by gunicorn | <http://localhost:5000> |
| `frontend` | Production Vite build served by nginx | <http://localhost:3000> |

Useful endpoints:

- SPA: <http://localhost:3000> (deep links such as `/about` and `/contact` reload correctly)
- Health check: <http://localhost:5000/api/v1/health>
- Auth API: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`

Run detached and follow logs:

```bash
docker compose up --build -d
docker compose logs -f backend frontend
```

### Database migrations

If the schema is not created automatically on start-up, apply the Alembic migrations
inside the running backend container:

```bash
docker compose exec backend flask db upgrade
```

To create a new revision after changing the models:

```bash
docker compose exec backend flask db migrate -m "describe change"
docker compose exec backend flask db upgrade
```

### Stopping / cleaning up

```bash
docker compose down            # stop and remove containers and the network
docker compose down -v         # also remove the pgdata volume (deletes all data)
docker compose build --no-cache frontend   # force a clean frontend rebuild
```

> Because `VITE_API_BASE_URL` is compiled into the bundle, changing it requires
> rebuilding the frontend image (`docker compose up --build`).

---

## 3. Local development without Docker

### Frontend (Vite dev server with HMR)

```bash
cd frontend
cp .env.example .env          # VITE_API_BASE_URL=http://localhost:5000/api/v1
npm install
npm run dev                   # http://localhost:5173
```

Other frontend scripts:

```bash
npm run build                 # production build into frontend/dist (what the image ships)
npm run preview               # serve the built dist locally
npm run test                  # Vitest + React Testing Library
```

When using the Vite dev server, set `FRONTEND_ORIGIN=http://localhost:5173` for the
backend so CORS allows the dev origin.

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FRONTEND_ORIGIN
flask db upgrade
flask run --port 5000
pytest                        # backend test suite
```

You can also run only the database in Docker while developing the API locally:

```bash
docker compose up -d db
```

---

## 4. Containerisation notes

- `frontend/Dockerfile` is a multi-stage build: `node:20-alpine` installs dependencies
  (`npm ci` when `package-lock.json` exists) and runs `npm run build`; `nginx:alpine`
  then serves only the `dist/` output from `/usr/share/nginx/html` on port **80**.
- `frontend/nginx.conf` defines a single server block with
  `try_files $uri $uri/ /index.html` so client-side routes (`/about`, `/contact`,
  unknown paths -> NotFound page) work on direct load/refresh. Hashed assets under
  `/assets/` get long-lived immutable cache headers while `index.html` is never cached.
- `frontend/.dockerignore` keeps `node_modules`, `dist`, test output, local env files and
  VCS artefacts out of the build context.
- Nothing is mounted into the frontend container at runtime - the image is a
  self-contained static bundle.
- No `container_name` keys are used in `docker-compose.yml`; verify with
  `docker compose config`.

---

## 5. Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS error in the browser console | Ensure `FRONTEND_ORIGIN` matches the URL in the address bar (`http://localhost:3000`) and restart the backend. |
| SPA loads but API calls go to the wrong host | Rebuild the frontend image after changing `VITE_API_BASE_URL` (`docker compose up --build frontend`). |
| `404` from nginx on refresh | Confirm `frontend/nginx.conf` was copied to `/etc/nginx/conf.d/default.conf` (rebuild without cache). |
| Backend cannot connect to the database | Wait for the `db` healthcheck; check `DATABASE_URL` host is `db` (the compose service name). |
| Port already in use | Change `FRONTEND_PORT`, `BACKEND_PORT` or `POSTGRES_PORT` in `.env`. |
