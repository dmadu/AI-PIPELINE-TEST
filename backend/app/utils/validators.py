"""Pure input validation helpers shared by the API schemas.

The module is deliberately framework free: it imports nothing from Flask or
from :mod:`app.utils.errors`, so the rules can be unit tested without an
application context and reused by any layer.

Return shapes (documented once, used everywhere)::

    validate_email_format(email) -> (errors: list[str], normalised: str | None)
    validate_username(username)  -> (errors: list[str], normalised: str | None)
    validate_password(password)  -> errors: list[str]

``errors`` is always a list holding one human readable message per failed rule
and is empty when the value is valid.  ``normalised`` is the cleaned value
(lowercased email, trimmed username) or ``None`` when validation failed.
"""

import re

from email_validator import EmailNotValidError, validate_email

__all__ = [
    "PASSWORD_RULES",
    "PASSWORD_MIN_LENGTH",
    "PASSWORD_SPECIAL_CHARACTERS",
    "USERNAME_MIN_LENGTH",
    "USERNAME_MAX_LENGTH",
    "EMAIL_MAX_LENGTH",
    "validate_email_format",
    "validate_username",
    "validate_password",
]

# --- password ---------------------------------------------------------------

PASSWORD_MIN_LENGTH = 8
PASSWORD_SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

# Compiled once at import time and reused by every call.
_UPPERCASE_PATTERN = re.compile(r"[A-Z]")
_DIGIT_PATTERN = re.compile(r"[0-9]")
_SPECIAL_PATTERN = re.compile("[" + re.escape(PASSWORD_SPECIAL_CHARACTERS) + "]")

#: The single source of truth for the password policy.  Each rule exposes a
#: stable ``name``, the human readable ``message`` returned on failure and the
#: ``test`` callable evaluating the rule against a string.
PASSWORD_RULES = (
    {
        "name": "min_length",
        "message": f"Password must be at least {PASSWORD_MIN_LENGTH} characters long.",
        "test": lambda value: len(value) >= PASSWORD_MIN_LENGTH,
    },
    {
        "name": "uppercase",
        "message": "Password must contain at least one uppercase letter.",
        "test": lambda value: bool(_UPPERCASE_PATTERN.search(value)),
    },
    {
        "name": "digit",
        "message": "Password must contain at least one digit.",
        "test": lambda value: bool(_DIGIT_PATTERN.search(value)),
    },
    {
        "name": "special",
        "message": (
            "Password must contain at least one special character "
            f"({PASSWORD_SPECIAL_CHARACTERS})."
        ),
        "test": lambda value: bool(_SPECIAL_PATTERN.search(value)),
    },
)

PASSWORD_REQUIRED_MESSAGE = "Password is required."

# --- username ---------------------------------------------------------------

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50  # matches the String(50) column on users.username
_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

USERNAME_REQUIRED_MESSAGE = "Username is required."
USERNAME_LENGTH_MESSAGE = (
    f"Username must be between {USERNAME_MIN_LENGTH} and {USERNAME_MAX_LENGTH} characters."
)
USERNAME_CHARSET_MESSAGE = (
    "Username may only contain letters, digits, underscores or hyphens."
)

# --- email ------------------------------------------------------------------

EMAIL_MAX_LENGTH = 255  # matches the String(255) column on users.email
EMAIL_REQUIRED_MESSAGE = "Email is required."
EMAIL_TOO_LONG_MESSAGE = f"Email must be at most {EMAIL_MAX_LENGTH} characters."


def validate_email_format(email):
    """Validate an email address and normalise it to lowercase.

    Uses the ``email-validator`` package with deliverability checks disabled so
    no DNS lookup happens during request handling.

    :param email: Raw value coming from the request body.
    :returns: ``(errors, normalised_email)``; ``errors`` is empty and
        ``normalised_email`` is the lowercased address when the value is valid,
        otherw"""
    pass
