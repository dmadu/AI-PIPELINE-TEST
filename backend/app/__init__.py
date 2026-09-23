import os
from flask import Flask
from app.extensions import db, migrate
from app.config import config_by_name

def create_app(config_name=None):
    """Application factory for Flask app."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/health")
    def health_check():
        return {"status": "healthy", "database": "configured"}, 200

    return app
