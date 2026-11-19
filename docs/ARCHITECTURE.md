# Architecture

## Goals

The design favours clear boundaries and simple deployment. Each component has one responsibility. State lives in the database, not in process memory.

## Components

### API

The API is a stateless HTTP server. It validates input, applies authentication, and calls service functions. It never contains business rules itself.

Requests pass through middleware in a fixed order. Middleware handles request IDs, logging, authentication, rate limits, and error formatting.

### Services

Services hold the business logic. They are plain functions that receive validated input and a database handle. They return data or throw typed errors.

Services do not know about HTTP. This keeps them easy to test and reusable from the worker.

### Data layer

The data layer owns all SQL. Queries are grouped by entity. Migrations are versioned files applied in order.

Transactions are opened by services and passed down. Nested transactions use savepoints.

### Worker

The worker consumes jobs from Redis. Jobs are small and idempotent. Each job records its result so repeats are safe.

Failed jobs retry with exponential backoff. After the final attempt a job moves to a dead-letter queue for manual review.

### Client

The client is a single-page application. It talks only to the API. It stores the access token in memory and the refresh token in a secure cookie.

## Data flow

A request arrives at the API. Middleware authenticates the caller. The controller validates the body and calls a service. The service reads or writes the database and may enqueue a job. The controller maps the result to a response.

## Error handling

Errors are typed. Each type maps to one HTTP status. Unexpected errors become a generic 500 response and are logged with a stack trace.

Error responses share one shape: a code, a human-readable message, and an optional details object.

## Security

Access tokens are short-lived. Refresh tokens rotate on every use. Passwords are hashed with a slow algorithm and a per-user salt.

All input is validated against a schema before use. Output is filtered so internal fields never leave the server.

## Scaling

The API scales horizontally behind a load balancer. The worker scales by adding processes. The database is the main bottleneck and is scaled with read replicas and connection pooling.

## Trade-offs

A single database keeps transactions simple but couples the components. A shared queue adds a dependency but removes slow work from request handling. These choices suit a small team and moderate traffic.
