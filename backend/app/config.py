import os
from dotenv import load

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/app_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pooling configurations with sensible defaults
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('SQLALCHEMY_POOL_SIZE', 5)),
        'max_overflow': int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 10)),
        'pool_timeout': int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.getenv('SQLALCHEMY_POOL_RECYCLE', 1800)),
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/app_test_db')

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
