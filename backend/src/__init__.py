import os
from flask import Flask
from src.extensions import db, migrate

def create_app(config_name=None):
    app = Flask(__name__)

    # Database configuration from environment variables
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    # Handle Render / Heroku postgres:// URIs if present
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Production-ready connection pooling parameters for PostgreSQL 16
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 10)),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 20)),
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800)),
        "pool_pre_ping": True,
    }

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/health")
    def health_check():
        return {"status": "healthy", "database": "configured"}, 200

    return app
