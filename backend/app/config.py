"""Environment-driven configuration classes.

All configuration comes from environment variables (``.env`` for local runs, the Docker
environment in containers). No secrets or database URLs are hard-coded here; only non-secret
local-development defaults are provided.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Load .env early so the class attributes below see the values during non-Docker runs.
load_dotenv()

__all__ = [
    "BaseConfig",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestingConfig",
    "get_config",
]

_DEV_FALLBACK_DATABASE_URI = "sqlite:///dev.sqlite3"
_DEFAULT_FRONTEND_ORIGIN = "http://localhost:3000"


def _normalise_database_url(url):
    """Return a SQLAlchemy-compatible database URL (``postgres://`` is legacy)."""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    """Settings shared by every environment."""

    ENV_NAME = "base"
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = _normalise_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", _DEFAULT_FRONTEND_ORIGIN)

    # JSON-only API: never fall back to HTML error pages for unknown media types.
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False

    @classmethod
    def init_app(cls, app):
        """Hook for per-environment setup; overridden where validation is required."""


class DevelopmentConfig(BaseConfig):
    """Local development: verbose logging and a usable default database."""

    ENV_NAME = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = (
        _normalise_database_url(os.getenv("DATABASE_URL")) or _DEV_FALLBACK_DATABASE_URI
    )


class ProductionConfig(BaseConfig):
    """Production: every secret must be supplied by the environment."""

    ENV_NAME = "production"
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        """Fail fast when a required production variable is missing."""
        required = ("SECRET_KEY", "JWT_SECRET_KEY", "SQLALCHEMY_DATABASE_URI")
        missing = [name for name in required if not app.config.get(name)]
        if missing:
            readable = {
                "SECRET_KEY": "SECRET_KEY",
                "JWT_SECRET_KEY": "JWT_SECRET_KEY",
                "SQLALCHEMY_DATABASE_URI": "DATABASE_URL",
            }
            names = ", ".join(readable[name] for name in missing)
            raise RuntimeError(f"Missing required environment variables: {names}")


class TestingConfig(BaseConfig):
    """Automated tests: in-memory SQLite, no external services required."""

    ENV_NAME = "testing"
    DEBUG = False
    TESTING = True
    SECRET_KEY = os.getenv("SECRET_KEY", "testing-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testing-jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
}


def get_config(name=None):
    """Return the config class matching ``name``, defaulting to :class:`DevelopmentConfig`."""
    key = (name or "development").strip().lower()
    return CONFIG_MAP.get(key, DevelopmentConfig)
