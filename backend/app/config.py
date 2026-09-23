import os
from dotenv import load

load.load_dotenv() if hasattr(load, 'load_dotenv') else None

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/postgres'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pooling configurations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 20)),
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 1800)),
        'pool_pre_ping': True,
    }
