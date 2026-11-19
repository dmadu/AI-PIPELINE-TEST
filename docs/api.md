# API Reference

## Conventions

All endpoints are under `/api/v1`. Requests and responses use JSON. Timestamps are ISO 8601 in UTC. Identifiers are UUID strings.

Authenticated endpoints require a bearer token in the `Authorization` header.

## Responses

Successful responses return the resource or a list wrapper. List wrappers contain the items, the total count, and the next cursor.

Error responses contain a code, a message, and optional details. The HTTP status matches the error class.

## Status codes

- 200 — request succeeded.
- 201 — resource created.
- 204 — succeeded with no body.
- 400 — validation failed.
- 401 — missing or invalid token.
- 403 — authenticated but not allowed.
- 404 — resource not found.
- 409 — conflict with current state.
- 429 — rate limit exceeded.
- 500 — unexpected server error.

## Authentication

- `POST /auth/register` — create an account. Returns the user and a token pair.
- `POST /auth/login` — exchange credentials for a token pair.
- `POST /auth/refresh` — exchange a refresh token for a new pair.
- `POST /auth/logout` — revoke the current refresh token.

## Users

- `GET /users/me` — return the current user.
- `PATCH /users/me` — update name, email, or preferences.
- `DELETE /users/me` — schedule account deletion.
- `GET /users/:id` — return a public profile.

## Items

- `GET /items` — list items with filters and pagination.
- `POST /items` — create an item.
- `GET /items/:id` — return one item.
- `PATCH /items/:id` — update mutable fields.
- `DELETE /items/:id` — soft-delete an item.

List filters include status, owner, and a free-text query. Results are sorted by creation time, newest first.

## Jobs

- `POST /jobs` — enqueue a background job.
- `GET /jobs/:id` — return job status and result.

Job status is one of queued, running, succeeded, or failed.

## Pagination

Lists use cursor pagination. Pass `limit` to set the page size and `cursor` to continue. The default limit is 25 and the maximum is 100.

## Rate limits

Anonymous callers get 60 requests per minute. Authenticated callers get 600. Limits are returned in response headers.

## Versioning

Breaking changes create a new version prefix. Old versions stay available for six months after a replacement ships.
