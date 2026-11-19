"""Application error type and the global Flask error handlers.

``ApiError`` is the single exception type raised by application code; the
handlers registered by :func:`register_error_handlers` translate it - together
with Werkzeug HTTP exceptions and any unexpected exception - into the shared
error envelope built in :mod:`app.utils.responses`.
"""

from werkzeug.exceptions import HTTPException

from app.utils.responses import error_response

__all__ = [
    "ApiError",
    "register_error_handlers",
    "VALIDATION_ERROR",
    "NOT_FOUND",
    "INTERNAL_ERROR",
]

VALIDATION_ERROR = "VALIDATION_ERROR"
NOT_FOUND = "NOT_FOUND"
INTERNAL_ERROR = "INTERNAL_ERROR"

#: Generic message returned for unhandled exceptions; never leaks internals.
INTERNAL_ERROR_MESSAGE = "An unexpected error occurred. Please try again later."

#: Machine readable codes for the HTTP statuses Werkzeug can raise.
_STATUS_CODES = {
    400: VALIDATION_ERROR,
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: NOT_FOUND,
    405: "METHOD_NOT_ALLOWED",
    406: "NOT_ACCEPTABLE",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: VALIDATION_ERROR,
    429: "TOO_MANY_REQUESTS",
}


def _code_for_status(status):
    """Return the machine readable error code matching an HTTP status code."""
    if status in _STATUS_CODES:
        return _STATUS_CODES[status]
    if status >= 500:
        return INTERNAL_ERROR
    return "HTTP_ERROR"


class ApiError(Exception):
    """Exception carrying everything needed to build an error envelope.

    :param code: Machine readable error code, defaults to ``VALIDATION_ERROR``.
    :param message: Human readable message shown to the API consumer.
    :param status: HTTP status code, defaults to ``400``.
    :param fields: Optional mapping of ``field -> message``.
    """

    code = VALIDATION_ERROR
    status = 400

    def __init__(self, code=VALIDATION_ERROR, message=None, status=400, fields=None):
        self.code = code or VALIDATION_ERROR
        self.message = message or "The request could not be processed."
        self.status = status or 400
        self.fields = dict(fields) if fields else None
        super().__init__(self.message)

    def to_dict(self):
        """Return the error payload as a plain dictionary (no Flask required)."""
        payload = {"code": self.code, "message": self.message}
        if self.fields:
            payload["fields"] = dict(self.fields)
        return {"error": payload}

    def to_response(self):
        """Serialise the error through :func:`app.utils.responses.error_response`."""
        return error_response(self.code, self.message, self.status, self.fields)

    def __repr__(self):  # pragma: no cover - debugging helper
        return f"<ApiError {self.code} status={self.status}>"


def register_error_handlers(app):
    """Register the ApiError / HTTPException / Exception handlers on ``app``.

    All three handlers answer with the shared error envelope so clients never
    receive Werkzeug's HTML pages or raw tracebacks.
    """

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        """Return the envelope described by the raised :class:`ApiError`."""
        return error.to_response()

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Convert a Werkzeug HTTP exception into the error envelope."""
        status = error.code or 500
        code = _code_for_status(status)
        if status >= 500:
            message = INTERNAL_ERROR_MESSAGE
        else:
            message = error.description or error.name
        return error_response(code, message, status)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        """Log and convert any unhandled exception into a 500 envelope."""
        if isinstance(error, HTTPException):
            return handle_http_exception(error)
        app.logger.error(
            "Unhandled exception while handling a request: %s",
            error.__class__.__name__,
            exc_info=True,
        )
        return error_response(INTERNAL_ERROR, INTERNAL_ERROR_MESSAGE, 500)

    return app
