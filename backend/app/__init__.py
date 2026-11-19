"""Application factory for the Flask REST API backend.

``create_app`` wires the shared extension singletons (db, migrate, bcrypt,
jwt, cors), imports the models package so Alembic/``create_all`` see the
metadata, registers the API blueprints and the global error handlers.
"""

import logging
import os

from flask import Blueprint, Flask, jsonify

from app import config as app_config
from app.extensions import bcrypt, cors, db, jwt, migrate

API_PREFIX = "/api/v1"

_CONFIG_CANDIDATES = {
    "development": ("DevelopmentConfig", "Development"),
    "dev": ("DevelopmentConfig", "Development"),
    "production": ("ProductionConfig", "Production"),
    "prod": ("ProductionConfig", "Production"),
    "testing": ("TestingConfig", "Testing"),
    "test": ("TestingConfig", "Testing"),
}


def _resolve_config(config_name=None):
    """Return the configuration object matching ``config_name``."""
    name = (
        config_name
        or os.getenv("FLASK_CONFIG")
        or os.getenv("FLASK_ENV")
        or "development"
    ).lower()

    mapping = getattr(app_config, "config", None)
    if isinstance(mapping, dict):
        resolved = mapping.get(name) or mapping.get("default")
        if resolved is not None:
            return resolved

    for attribute in _CONFIG_CANDIDATES.get(name, ("DevelopmentConfig", "Development")):
        resolved = getattr(app_config, attribute, None)
        if resolved is not None:
            return resolved

    raise RuntimeError(f"Unknown configuration name: {name}")


def _configure_logging(app):
    """Attach a stream handler and set the level from the config/debug flag."""
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        )
        app.logger.addHandler(handler)
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    app.logger.setLevel(app.config.get("LOG_LEVEL", level))


def _init_extensions(app):
    """Initialise every shared extension singleton on ``app``."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    origin = app.config.get("FRONTEND_ORIGIN") or "*"
    cors.init_app(app, resources={r"/api/*": {"origins": origin}})


def _iter_api_modules():
    """Yield the available API modules, tolerating not-yet-created ones."""
    for module_name in ("health", "auth"):
        try:
            module = __import__(f"app.api.{module_name}", fromlist=[module_name])
        except ImportError:
            continue
        yield module


def _register_blueprints(app):
    """Register every blueprint found in ``app.api`` under ``/api/v1``."""
    for module in _iter_api_modules():
        for candidate in vars(module).values():
            if not isinstance(candidate, Blueprint):
                continue
            if candidate.name in app.blueprints:
                continue
            prefix = candidate.url_prefix or ""
            if not prefix.startswith(API_PREFIX):
                prefix = f"{API_PREFIX}{prefix}"
            app.register_blueprint(candidate, url_prefix=prefix)


def _ensure_health_route(app):
    """Guarantee that ``GET /api/v1/health`` always responds."""
    rules = {str(rule.rule) for rule in app.url_map.iter_rules()}
    if f"{API_PREFIX}/health" in rules:
        return

    try:
        from app.utils.responses import success
    except ImportError:  # pragma: no cover - utils always present
        success = None

    @app.get(f"{API_PREFIX}/health")
    def health_check():  # pragma: no cover - trivial fallback
        payload = {"status": "ok"}
        if success is not None:
            return success(payload)
        return jsonify({"data": payload}), 200


def _register_error_handlers(app):
    """Register the shared error handlers from ``app.utils.errors``."""
    try:
        from app.utils.errors import register_error_handlers
    except ImportError:  # pragma: no cover - utils always present
        return
    register_error_handlers(app)


def create_app(config_name=None):
    """Create and configure the Flask application instance."""
    app = Flask(__name__)

    config_object = _resolve_config(config_name)
    app.config.from_object(config_object)
    init_app = getattr(config_object, "init_app", None)
    if callable(init_app):
        init_app(app)

    _configure_logging(app)
    _init_extensions(app)

    # Import models so SQLAlchemy metadata is populated for Alembic/create_all.
    from app import models  # noqa: F401  pylint: disable=unused-import

    _register_blueprints(app)
    _ensure_health_route(app)
    _register_error_handlers(app)

    @app.shell_context_processor
    def _shell_context():  # pragma: no cover - developer convenience
        return {"db": db, "User": models.User}

    app.logger.debug("Application created with config %s", config_object)
    return app
