"""Environment driven configuration classes.

All settings come from environment variables; no secrets are committed.
"""

import os
from datetime import timedelta


def _normalise_database_url(url):
    """Return a SQLAlchemy 2.x friendly database URL."""
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class BaseConfig:
    """Settings shared by every environment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_DATABASE_URI = _normalise_database_url(
        os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/appdb")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    JSON_SORT_KEYS = False
    LOG_LEVEL = "INFO"
    PROPAGATE_EXCEPTIONS = False


class DevelopmentConfig(BaseConfig):
    """Local development settings."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
    """Container / production settings."""

    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(BaseConfig):
    """Pytest settings backed by an in-memory SQLite database."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    SECRET_KEY = "testing-secret-key"
    JWT_SECRET_KEY = "testing-jwt-secret-key"
    LOG_LEVEL = "DEBUG"
    BCRYPT_LOG_ROUNDS = 4


_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
}


def get_config(config_name=None):
    """Resolve a configuration class from a name or the environment."""
    name = (config_name or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development")
    return _CONFIG_MAP.get(str(name).lower(), DevelopmentConfig)
