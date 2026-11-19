# Project

A small service with a REST API, background jobs, and a web client.

## Overview

The system has three parts. The API handles HTTP requests. The worker runs queued jobs. The client renders the user interface.

All parts share one database and one message queue. Each part can be deployed on its own.

## Requirements

- Runtime: Node.js 20 or newer.
- Database: PostgreSQL 15 or newer.
- Queue: Redis 7 or newer.
- Package manager: npm.

## Setup

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Fill in the database and Redis URLs.
4. Install dependencies with npm.
5. Run database migrations.
6. Start the API, the worker, and the client.

## Configuration

Configuration comes from environment variables. The application reads them once at startup. Missing required values stop the process with a clear error.

Key variables:

- `DATABASE_URL` — PostgreSQL connection string.
- `REDIS_URL` — Redis connection string.
- `PORT` — API listen port.
- `LOG_LEVEL` — one of debug, info, warn, error.
- `JWT_SECRET` — signing key for access tokens.

## Scripts

- `dev` — run all services with hot reload.
- `build` — compile TypeScript to JavaScript.
- `start` — run the compiled API.
- `test` — run unit and integration tests.
- `lint` — check formatting and lint rules.
- `migrate` — apply pending migrations.

## Project layout

- `src/api` — HTTP routes and controllers.
- `src/services` — business logic.
- `src/db` — schema, migrations, and queries.
- `src/worker` — job handlers.
- `src/shared` — config, logging, and errors.
- `tests` — test suites.
- `docs` — written documentation.

## Documentation

See `docs/architecture.md` for the system design. See `docs/api.md` for endpoint details. See `docs/operations.md` for deployment and monitoring. See `CONTRIBUTING.md` for the development workflow.

## License

MIT.
