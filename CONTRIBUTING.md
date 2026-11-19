# Contributing

## Workflow

Create a branch from `main` for each change. Keep branches short-lived and focused on one topic.

Open a pull request when the change is ready. Describe the problem, the solution, and the testing performed.

## Commits

Use conventional commit messages. The type prefix is one of feat, fix, docs, refactor, test, or chore. Keep the subject under 72 characters.

## Code style

Formatting and lint rules are enforced by tooling. Run the lint script before pushing. Do not disable rules without a comment explaining why.

Prefer small functions with clear names. Avoid shared mutable state. Keep business logic out of HTTP handlers.

## Tests

Every change needs tests. Unit tests cover service logic. Integration tests cover routes against a test database.

Tests must be deterministic and independent. Use fixtures instead of shared global data.

## Reviews

Each pull request needs one approval. Reviewers check correctness, tests, naming, and documentation. Authors respond to every comment before merging.

## Documentation

Update the relevant document whenever behaviour changes. API changes require an update to the API reference. Design changes require an update to the architecture document.

## Releases

Merges to `main` trigger a staging deployment. Production releases are tagged and deployed manually after staging checks pass.
