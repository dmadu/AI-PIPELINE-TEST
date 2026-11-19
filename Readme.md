# Project

Full-stack application: a **Flask 3 REST API** (Python 3.11, SQLAlchemy, Flask-Migrate,
Flask-JWT-Extended, Flask-Bcrypt) backed by **PostgreSQL 16**, with a React 19 frontend
(added in a later phase). Everything is orchestrated with Docker Compose.

## Project structure

```text
project/
  backend/            # Flask service root
    app/              # application package (create_app, config, extensions)
      api/            # blueprints: health.py, auth.py
      models/         # SQLAlchemy models (user.py)
      schemas/        # request validation helpers
      utils/          # errors.py, responses.py, validators.py
    migrations/       # Flask-Migrate / Alembic revisions
    tests/            # pytest suite
    Dockerfile
    requirements.txt
    wsgi.py
    .env.example
  frontend/           # React 19 service root (later phase)
  docs/
  docker-compose.yml
  .env.example
  Readme.md
```

## API

- Base path: `/api/v1`
- Health check: `GET /api/v1/health`
- Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Success envelope: `{"data": { ... }}`
- Error envelope: `{"error": {"code": "...", "message": "...", "fields": { ... }}}`

## Configuration

All configuration is read from environment variables (see `backend/app/config.py`).
No secrets are committed or baked into the Docker image.

| Variable           | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| `FLASK_APP`        | CLI entrypoint, `wsgi.py`                                   |
| `FLASK_ENV`        | `development` \| `production` \| `testing`                  |
| `CONFIG_NAME`      | Configuration class selector (same values as `FLASK_ENV`)   |
| `SECRET_KEY`       | Flask signing secret                                        |
| `JWT_SECRET_KEY`   | JWT signing secret                                          |
| `DATABASE_URL`     | SQLAlchemy URL, e.g. `postgresql://appuser:apppassword@db:5432/appdb` |
| `FRONTEND_ORIGIN`  | Allowed CORS origin, e.g. `http://localhost:3000`           |
| `POSTGRES_USER`    | Postgres role created by the `db` service                   |
| `POSTGRES_PASSWORD`| Postgres password                                           |
| `POSTGRES_DB`      | Postgres database name                                      |

> Inside Docker Compose the database host is the **service name `db`**, not `localhost`.

---

## Running with Docker Compose

Prerequisites: Docker Engine with the Compose v2 plugin.

1. Create your local environment file from the template and edit the secrets:

   ```bash
   cp .env.example .env
   ```

2. Build the images and start the stack (PostgreSQL 16 + Flask API on gunicorn):

   ```bash
   docker compose up --build
   ```

   The `backend` service waits until the `db` service reports **healthy**
   (`pg_isready`) before it starts.

3. Apply the database migrations (see the next section) and verify the API:

   ```bash
   curl http://localhost:5000/api/v1/health
   # {"data":{"status":"ok", ...}}
   ```

Useful commands:

```bash
docker compose config            # validate / render the merged configuration
docker compose ps                # service status and health
docker compose logs -f backend   # follow gunicorn logs
docker compose down              # stop the stack (pgdata volume is preserved)
docker compose down -v           # stop and DELETE the database volume
```

Data is stored in the named volume **`pgdata`**, so restarting the stack keeps
all rows. No service declares a `container_name`.

---

## Database migrations

Migrations are Flask-Migrate (Alembic) revisions located in `backend/migrations/`
and are executed **inside the running backend container**, where `DATABASE_URL`
points at the `db` service. `FLASK_APP=wsgi.py` is already set in the image and in
`docker-compose.yml`, so the `flask` CLI resolves the application factory
automatically.

Apply all pending migrations (creates the `users` table from
`0001_create_users_table`):

```bash
docker compose exec backend flask db upgrade
```

Generate a new revision after changing a model:

```bash
docker compose exec backend flask db migrate -m "add some column"
docker compose exec backend flask db upgrade
```

Other handy migration commands:

```bash
docker compose exec backend flask db current     # current revision
docker compose exec backend flask db history     # revision history
docker compose exec backend flask db downgrade -1
```

> If `FLASK_APP` is ever unset in your shell, prefix the command:
> `docker compose exec -e FLASK_APP=wsgi.py backend flask db upgrade`.

Verify the schema directly in the database container:

```bash
docker compose exec db psql -U appuser -d appdb -c "\dt"
docker compose exec db psql -U appuser -d appdb -c "\d users"
```

---

## Local development without Docker (optional)

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set DATABASE_URL to a reachable Postgres host
export FLASK_APP=wsgi.py
flask db upgrade
flask run --port 5000
```

## Tests

The backend test suite uses the `TestingConfig` (SQLite in-memory), so no
PostgreSQL instance is required.

```bash
# locally
cd backend && pytest

# inside the container
docker compose exec backend pytest
```

> Note: `tests/` is excluded from the runtime image via `backend/.dockerignore`;
> run them locally, or mount the backend directory when you want to run pytest
> inside the container.
