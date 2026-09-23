import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load

load()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        # Default configuration using environment variables
        database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        # Connection pooling settings
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_size": int(os.environ.get("SQLALCHEMY_POOL_SIZE", 10)),
            "pool_recycle": int(os.environ.get("SQLALCHEMY_POOL_RECYCLE", 3600)),
            "pool_pre_ping": True,
            "max_overflow": int(os.environ.get(
                "SQLALCHEMY_MAX_OVERFLOW", 2
            )),
        }
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/health/db", methods=["GET"])
    def db_health_check():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}, 200
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}, 500

    return app
