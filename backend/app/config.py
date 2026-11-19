"""Environment driven configuration classes."""

import os
from datetime import timedelta

try:  # python-dotenv is optional at runtime (Docker injects real env vars).
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv always present in requirements
    pass


class BaseConfig:
    """Settings shared by every environment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/appdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False


class DevelopmentConfig(BaseConfig):
    """Local development settings."""

    DEBUG = True
    BCRYPT_LOG_ROUNDS = 12


class ProductionConfig(BaseConfig):
    """Production settings."""

    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13


class TestingConfig(BaseConfig):
    """Settings used by the pytest suite (in-memory SQLite)."""

    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    BCRYPT_LOG_ROUNDS = 4
    JWT_SECRET_KEY = "testing-jwt-secret-key"
    SECRET_KEY = "testing-secret-key"
    PROPAGATE_EXCEPTIONS = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(config_name=None):
    """Resolve a configuration class from a name or the environment."""
    if isinstance(config_name, type):
        return config_name

    name = (
        config_name
        or os.getenv("APP_ENV")
        or os.getenv("FLASK_ENV")
        or "development"
    ).lower()
    return CONFIG_MAP.get(name, DevelopmentConfig)
