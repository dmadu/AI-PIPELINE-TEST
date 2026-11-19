"""Shared pytest fixtures for the backend test-suite.

The fixtures build the Flask application through the existing application
factory using the project's *testing* configuration, which points SQLAlchemy at
an in-memory SQLite database.  As a result the suite never needs PostgreSQL,
Docker or a ``.env`` file, and every test starts from a clean schema.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure ``backend/`` is importable when pytest is run from any directory.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Deterministic, secret-free environment for the test run.  Every value below is
# a placeholder and the database URL keeps the suite on SQLite in-memory even if
# the configuration falls back to reading the environment directly.
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("FLASK_CONFIG", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "testing-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "testing-jwt-secret-key")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:3000")

from app import create_app  # noqa: E402  (import after sys.path/env setup)
from app.extensions import db as _db  # noqa: E402
from app.models.user import User  # noqa: F401,E402  (registers table metadata)


def _testing_config_class():
    """Return the testing configuration class declared in ``app.config``."""
    try:
        from app import config as config_module
    except ImportError:  # pragma: no cover - config module always exists
        return None
    for name in ("TestingConfig", "Testing"):
        candidate = getattr(config_module, name, None)
        if isinstance(candidate, type):
            return candidate
    return None


def _create_testing_app():
    """Build the application with the project's testing configuration.

    ``create_app`` may take either a configuration name or a configuration
    class depending on the factory implementation, so both forms are tried and
    the first application reporting ``TESTING`` is used.
    """
    candidates = ["testing", "Testing", "TestingConfig"]
    config_class = _testing_config_class()
    if config_class is not None:
        candidates.append(config_class)

    first_application = None
    last_error = None
    for candidate in candidates:
        try:
            application = create_app(candidate)
        except Exception as exc:  # pragma: no cover - factory signature probing
            last_error = exc
            continue
        if application.config.get("TESTING"):
            return application
        if first_application is None:
            first_application = application

    if first_application is not None:  # pragma: no cover - defensive fallback
        first_application.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        )
        return first_application

    if last_error is not None:  # pragma: no cover - surfaces real factory errors
        raise last_error
    raise RuntimeError("create_app did not return an application in testing mode")


@pytest.fixture()
def app():
    """Function-scoped Flask application bound to a fresh in-memory schema."""
    application = _create_testing_app()
    context = application.app_context()
    context.push()
    _db.create_all()
    try:
        yield application
    finally:
        _db.session.remove()
        _db.drop_all()
        context.pop()


@pytest.fixture()
def client(app):
    """Test client for calling the ``/api/v1`` endpoints."""
    return app.test_client()


@pytest.fixture()
def db(app):
    """Shared SQLAlchemy extension, cleared of all rows after every test."""
    yield _db
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()
    _db.session.remove()
