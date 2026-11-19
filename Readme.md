# Items API

A small FastAPI service with in-memory CRUD for items.

## Install

```
pip install -r requirements.txt
```

## Run

```
uvicorn src.main:app --reload
```

Docs are served at `/docs`.

## Test

```
pytest
```

## Endpoints

- `GET /health` - liveness check.
- `GET /items` - list items.
- `POST /items` - create an item.
- `GET /items/{item_id}` - fetch one item.
- `PUT /items/{item_id}` - replace an item.
- `DELETE /items/{item_id}` - remove an item.

## Notes

- Storage is a process-local dict, so data resets on restart.
- Validation is handled by Pydantic models.
- Missing resources return HTTP 404 with a JSON detail message.
