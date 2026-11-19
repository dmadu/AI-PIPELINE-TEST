"""Request payload validation for the auth endpoints."""

from ..utils.errors import ApiError
from ..utils.validators import (
    validate_email_format,
    validate_password,
    validate_username,
)

VALIDATION_MESSAGE = "The submitted data is invalid."


def validate_register_payload(payload):
    """Validate the registration body and return cleaned values."""
    data = _require_object(payload)
    fields = {}

    email_input = _get_string(data, "email")
    username_input = _get_string(data, "username")
    password_input = data.get("password") if isinstance(data.get("password"), str) else ""

    email_errors = validate_email_format(email_input)
    if email_errors:
        fields["email"] = " ".join(email_errors)

    normalised_email = email_input.lower()

    username_error = validate_username(username_input)
    if username_error:
        fields["username"] = username_error

    password_errors = validate_password(password_input)
    if password_errors:
        fields["password"] = " ".join(password_errors)

    if fields:
        raise ApiError("VALIDATION_ERROR", VALIDATION_MESSAGE, 400, fields)

    return {
        "email": normalised_email,
        "username": username_input,
        "password": password_input,
    }


def validate_login_payload(payload):
    """Ensure identifier and password are provided for login."""
    data = _require_object(payload)
    identifier = _get_string(data, "identifier")
    password = _get_string(data, "password")

    fields = {}
    if not identifier:
        fields["identifier"] = "Identifier is required."
    if not password:
        fields["password"] = "Password is required."

    if fields:
        raise ApiError("VALIDATION_ERROR", VALIDATION_MESSAGE, 400, fields)

    return {"identifier": identifier, "password": password}


def _require_object(payload):
    if not isinstance(payload, dict):
        raise ApiError("VALIDATION_ERROR", VALIDATION_MESSAGE, 400)
    return payload


def _get_string(data, key):
    val = data.get(key)
    return val.strip() if isinstance(val, str) else ""
