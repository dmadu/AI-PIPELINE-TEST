import os
from dotenv import load

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pooling configuration for PostgreSQL 16
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 10)),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 20)),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", 30)),
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800)),
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/app_dev"
    )

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/app_test"
    )

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
