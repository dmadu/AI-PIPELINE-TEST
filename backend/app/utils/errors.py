"""Application error type and the single app-level error handler set."""

from flask import current_app
from werkzeug.exceptions import HTTPException

from .responses import error_response

_HTTP_CODE_MAP = {
    400: "VALIDATION_ERROR",
    401: "TOKEN_MISSING",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    415: "VALIDATION_ERROR",
}


class ApiError(Exception):
    """Raised by routes/helpers to produce the documented error envelope."""

    def __init__(self, code, message, status=400, fields=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.fields = fields or None

    def to_dict(self):
        """Return the error envelope body for this error."""
        payload = {"code": self.code, "message": self.message}
        if self.fields:
            payload["fields"] = self.fields
        return {"error": payload}

    def __repr__(self):  # pragma: no cover - debugging helper
        return f"<ApiError {self.code} status={self.status}>"


def register_error_handlers(app):
    """Register the handlers converting exceptions into the error envelope."""

    @app.errorhandler(ApiError)
    def _handle_api_error(error):  # pragma: no cover - thin wrapper
        return error_response(error.code, error.message, error.status, error.fields)

    @app.errorhandler(HTTPException)
    def _handle_http_exception(error):
        code = _HTTP_CODE_MAP.get(error.code, "HTTP_ERROR")
        message = error.description or error.name
        return error_response(code, message, error.code or 500)

    @app.errorhandler(Exception)
    def _handle_unexpected_exception(error):
        current_app.logger.exception("Unhandled exception: %s", error.__class__.__name__)
        return error_response("INTERNAL_ERROR", "An unexpected error occurred", 500)


def register_jwt_handlers(jwt):
    """Register custom response loaders for JWT errors."""

    @jwt.expired_token_loader
    def _handle_expired_token(jwt_header, jwt_payload):
        return error_response("TOKEN_EXPIRED", "The token has expired", 401)

    @jwt.invalid_token_loader
    def _handle_invalid_token(reason):
        return error_response("TOKEN_INVALID", f"Invalid token: {reason}", 401)

    @jwt.unauthorized_loader
    def _handle_missing_token(reason):
        return error_response("TOKEN_MISSING", f"Missing authorization header: {reason}", 401)

    @jwt.revoked_token_loader
    def _handle_revoked_token(jwt_header, jwt_payload):
        return error_response("TOKEN_REVOKED", "The token has been revoked", 401)
