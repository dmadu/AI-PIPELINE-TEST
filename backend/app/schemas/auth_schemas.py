"""Request schemas for the authentication endpoints.

These helpers parse the raw JSON body, apply the shared validators from
``app.utils.validators`` and raise a 400 ``VALIDATION_ERROR`` ApiError carrying
per-field messages. Routes stay thin and never duplicate validation logic.
"""

from ..utils.errors import ApiError
from ..utils.validators import validate_email_format, validate_password, validate_username

VALIDATION_ERROR_CODE = "VALIDATION_ERROR"
VALIDATION_ERROR_MESSAGE = "Validation failed"


def _as_text(value):
    """Return a trimmed string for scalar input, otherwise an empty string."""
    if isinstance(value, str):
        return value.strip()
    return ""


def _join(messages):
    """Collapse a list of rule messages into a single field message."""
    return " ".join(messages)


def parse_register_request(payload):
    """Validate a registration body and return cleaned ``email``/``username``/``password``.

    Raises:
        ApiError: 400 VALIDATION_ERROR when the body shape or any field is invalid.
    """
    if not isinstance(payload, dict):
        raise ApiError(
            VALIDATION_ERROR_CODE,
            "Request body must be a JSON object",
            400,
        )

    username = _as_text(payload.get("username"))
    email = _as_text(payload.get("email"))
    raw_password = payload.get("password")

    fields = {}

    username_errors = validate_username(username)
    if username_errors:
        fields["username"] = _join(username_errors)

    email_errors = validate_email_format(email)
    if email_errors:
        fields["email"] = _join(email_errors)

    if raw_password is None:
        fields["password"] = "Password is required"
    elif not isinstance(raw_password, str):
        fields["password"] = "Password must be a string"
    else:
        password_errors = validate_password(raw_password)
        if password_errors:
            fields["password"] = _join(password_errors)

    if fields:
        raise ApiError(VALIDATION_ERROR_CODE, VALIDATION_ERROR_MESSAGE, 400, fields)

    return {
        "username": username,
        "email": email.lower(),
        "password": raw_password,
    }
