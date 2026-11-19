# Task API

A small REST API for managing tasks, built with FastAPI.

## Features

- Create, read, update and delete tasks.
- Filter the task list by completion state.
- In-memory, thread-safe storage.
- Automatic OpenAPI docs at `/docs`.

## Setup

1. Create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the server: `uvicorn app.main:app --reload`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Service liveness check |
| GET | /tasks | List tasks, optional `completed` filter |
| POST | /tasks | Create a task |
| GET | /tasks/{id} | Fetch one task |
| PATCH | /tasks/{id} | Partially update a task |
| DELETE | /tasks/{id} | Delete a task |

## Tests

Run `pytest` from the project root.

## Notes

Data lives in process memory and is lost on restart. Swap the storage module for a database layer to persist data.
