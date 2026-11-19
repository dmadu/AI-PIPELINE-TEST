"""Application factory for the Flask API service."""

import logging
import sys

from flask import Flask

from .config import get_config
from .extensions import bcrypt, cors, db, jwt, migrate
from .utils.errors import register_error_handlers

try:  # pragma: no cover - optional dependency for local (non-Docker) runs
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _configure_logging(app):
    """Attach a single StreamHandler and honour the configured log level."""
    level = getattr(logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO)
    if not app.logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
        )
        app.logger.addHandler(handler)
    app.logger.setLevel(level)
    app.logger.propagate = False


def create_app(config_name=None):
    """Create and configure a Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    _configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}},
        supports_credentials=False,
    )

    # Imported so Flask-Migrate/metadata sees the model.
    from .models.user import User  # noqa: F401  pylint: disable=unused-import

    from .api.auth import auth_bp
    from .api.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)

    register_error_handlers(app)

    return app
