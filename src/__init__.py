from flask import Flask
from src.config import Config
from src.extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    return app
