# Task API

A small REST API for managing tasks, built with FastAPI and Pydantic v2.
Data is kept in a thread-safe in-memory store, so it resets on restart.

## Layout

- `src/models.py` - request and response models.
- `src/storage.py` - in-memory store and `NotFound` error.
- `src/app.py` - routes and HTTP error mapping.
- `tests/test_app.py` - API tests.

## Install

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```
uvicorn src.app:app --reload
```

Interactive docs are served at `/docs`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| POST | `/tasks` | Create a task (201) |
| GET | `/tasks` | List tasks, optional `status` filter |
| GET | `/tasks/{id}` | Fetch one task |
| PATCH | `/tasks/{id}` | Partial update |
| DELETE | `/tasks/{id}` | Delete a task (204) |

## Behaviour notes

- `status` must be `todo`, `doing` or `done`.
- Titles are required and limited to 200 characters.
- PATCH only applies fields that are sent; `updated_at` always changes.
- Unknown ids return 404; invalid bodies return 422.
- Ids are sequential integers starting at 1.

## Tests

```
pytest
```

## Possible next steps

Swap the store for a database, add pagination, and add authentication.
