"""Application factory for the Flask API service."""

import logging
import sys

from flask import Flask

from .config import get_config
from .extensions import bcrypt, cors, db, jwt, migrate
from .utils.errors import register_error_handlers


def _configure_logging(app):
    """Attach a stream handler and apply the configured log level."""
    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    if app.debug:
        level = logging.DEBUG

    if not app.logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        )
        app.logger.addHandler(handler)

    app.logger.setLevel(level)


def _register_extensions(app):
    """Initialise the shared extension singletons on the app."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}},
        supports_credentials=False,
    )


def _register_blueprints(app):
    """Register every API blueprint."""
    from .api.auth import auth_bp
    from .api.health import health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)


def create_app(config_name=None):
    """Build and configure a Flask application instance.

    ``config_name`` accepts an environment name (``development``, ``testing``,
    ``production``) or a configuration class/object.
    """
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    _configure_logging(app)
    _register_extensions(app)

    # Imported so Flask-Migrate/Alembic can discover the metadata.
    from .models.user import User  # noqa: F401  pylint: disable=