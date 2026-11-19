# Operations

## Environments

There are three environments: development, staging, and production. Staging mirrors production configuration with smaller resources.

## Deployment

Each component builds into a container image. Images are tagged with the commit hash. Deployments are rolling, with health checks gating each step.

Migrations run as a separate step before the new version starts. Migrations must be backward compatible so old and new code can run together.

## Health checks

The API exposes a liveness endpoint and a readiness endpoint. Liveness confirms the process responds. Readiness confirms the database and queue are reachable.

## Logging

Logs are structured JSON written to standard output. Every line includes a timestamp, level, message, and request ID. Sensitive fields are redacted before writing.

## Metrics

The service exports request counts, latency percentiles, error rates, queue depth, and job duration. Dashboards track these per environment.

## Alerts

Alerts fire on elevated error rates, slow responses, growing queue depth, and failed migrations. Each alert links to a runbook entry.

## Backups

The database is backed up nightly with point-in-time recovery enabled. Restores are tested each quarter in staging.

## Incident response

On an incident, first confirm scope with dashboards. Then roll back the most recent deployment if timing matches. Record findings in a short write-up within two working days.
