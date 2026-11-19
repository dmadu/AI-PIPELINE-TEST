"""Application factory for the Flask API service."""

import logging

from flask import Flask

from .config import get_config
from .extensions import bcrypt, cors, db, jwt, migrate
from .utils.errors import register_error_handlers, register_jwt_handlers


def create_app(config_name=None):
    """Create and configure a Flask application instance.

    :param config_name: one of 'development', 'production', 'testing'.
    """
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    _configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)

    register_error_handlers(app)
    register_jwt_handlers(app)

    return app


def _configure_logging(app):
    """Attach a stream handler and pick the log level from the config."""
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        )
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG if app.config.get("DEBUG") else logging.INFO)


def _register_extensions(app):
    """Initialise the shared extension singletons."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}},
        supports_credentials=False,
    )

    # Imported for side effects so Flask-Migrate/SQLAlchemy see the metadata.
    from .models import user  # noqa: F401  pylint: disable=unused-import


def _register_blueprints(app):
    """Register the API blueprints under the /api/v1 base path."""
    from .api.auth import auth_bp
    from .api.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
