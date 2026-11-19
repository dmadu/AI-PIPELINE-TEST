"""Application factory for the Flask API service.

Exposes :func:`create_app`, which builds a configured Flask application using the
application-factory + blueprint pattern described in ``docs/ARCHITECTURE.md``.

Note: ``app/utils/errors.py`` (``ApiError`` + ``register_error_handlers``) is delivered by a
later Phase 1 task. Until it exists, this module wires a minimal, behaviour-compatible set of
error handlers that produce the documented error envelope; the guarded import below picks up the
shared utility automatically as soon as it lands, with no response-body change.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .config import get_config
from .extensions import bcrypt, cors, db, jwt, migrate

__all__ = ["create_app"]

_LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
_HANDLER_FLAG = "_api_stream_handler"

_HTTP_ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "TOKEN_INVALID",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "VALIDATION_ERROR",
}


def create_app(config_name=None):
    """Create and configure a Flask application instance.

    :param config_name: one of ``development``, ``production`` or ``testing``. When omitted the
        value of ``FLASK_ENV`` / ``APP_ENV`` is used, falling back to ``development``.
    :return: the configured :class:`flask.Flask` application.
    """
    load_dotenv()  # No-op when the variables already come from the Docker environment.

    resolved_name = (
        config_name
        or os.getenv("FLASK_ENV")
        or os.getenv("APP_ENV")
        or "development"
    )
    config_class = get_config(resolved_name)

    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # JSON-only API: keep key order as produced by the endpoints.
    app.json.sort_keys = False

    _configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    app.logger.debug("Application created using %s", config_class.__name__)
    return app


def _configure_logging(app):
    """Attach exactly one StreamHandler to ``app.logger`` at the configured level."""
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    app.logger.setLevel(level)

    for handler in app.logger.handlers:
        if getattr(handler, _HANDLER_FLAG, False):
            handler.setLevel(level)
            return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    handler.setLevel(level)
    setattr(handler, _HANDLER_FLAG, True)
    app.logger.handlers = [handler]
    app.logger.propagate = False


def _register_extensions(app):
    """Initialise every extension singleton against the application."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )


def _register_blueprints(app):
    """Register API blueprints (imported locally to avoid circular imports)."""
    from .api.health import health_bp

    app.register_blueprint(health_bp)


def _register_error_handlers(app):
    """Wire error handling through a single registration point."""
    try:  # pragma: no cover - exercised once app/utils/errors.py exists.
        from .utils.errors import register_error_handlers
    except ImportError:
        register_error_handlers = None

    if register_error_handlers is not None:  # pragma: no cover - see note above.
        register_error_handlers(app)
        return

    @app.errorhandler(HTTPException)
    def _handle_http_exception(exc):
        """Convert Werkzeug HTTP errors into the documented error envelope."""
        code = _HTTP_ERROR_CODES.get(exc.code, "HTTP_ERROR")
        return _error_envelope(code, exc.description, exc.code or 500)

    @app.errorhandler(Exception)
    def _handle_unexpected_exception(exc):
        """Convert unexpected errors into a 500 error envelope without leaking details."""
        app.logger.exception("Unhandled exception: %s", exc)
        return _error_envelope("INTERNAL_ERROR", "An unexpected error occurred.", 500)


def _error_envelope(code, message, status):
    """Build the standard ``{"error": {...}}`` response body."""
    return jsonify({"error": {"code": code, "message": message}}), status
