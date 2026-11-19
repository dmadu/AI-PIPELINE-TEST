"""Parsing and validation helpers for the authentication request payloads.

Every field rule is delegated to :mod:`app.utils.validators`; this module only
normalises the raw JSON body (presence, type, whitespace, email casing) and
collects all failures into a single ``VALIDATION_ERROR`` :class:`ApiError`.
"""

import inspect

from app.utils.errors import ApiError
from app.utils.validators import (
    validate_email_format,
    validate_password,
    validate_username,
)

try:  # pragma: no cover - depends on the validators module layout
    from app.utils.validators import PASSWORD_RULES
except ImportError:  # pragma: no cover
    PASSWORD_RULES = ()

VALIDATION_CODE = "VALIDATION_ERROR"
VALIDATION_MESSAGE = "Validation failed"

_LABELS = {
    "email": "Email",
    "username": "Username",
    "password": "Password",
    "identifier": "Username or email",
}


def parse_register_payload(data):
    """Validate a registration body and return ``{email, username, password}``.

    ``email`` is trimmed and lowercased, ``username`` is trimmed with its case
    preserved and ``password`` is returned untouched. Raises an ``ApiError``
    with code ``VALIDATION_ERROR`` (HTTP 400) listing every invalid field.
    """
    payload = _as_object(data)
    fields = {}

    email = _string_field(payload, "email", fields)
    username = _string_field(payload, "username", fields)
    password = _string_field(payload, "password", fields, strip=False)

    if email is not None:
        email = email.lower()
        _collect(fields, "email", _messages(validate_email_format(email)))
    if username is not None:
        _collect(fields, "username", _messages(validate_username(username)))
    if password is not None:
        password_messages = _password_messages(password)
        if password_messages:
            fields["password"] = password_messages

    if fields:
        raise _validation_error(fields)

    return {"email": email, "username": username, "password": password}


def parse_login_payload(data):
    "