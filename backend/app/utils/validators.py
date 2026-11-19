"""Server-side validation rules shared by the API layer.

Each validator returns a list of human readable messages; an empty list means
the value is valid.
"""

import re

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 255

SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

PASSWORD_RULES = (
    "Password must be at least 8 characters long",
    "Password must contain at least one uppercase letter",
    "Password must contain at least one digit",
    "Password must contain at least one special character "
    "(!@#$%^&*()-_=+[]{};:,.<>?/|~)",
)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_FALLBACK_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


def validate_username(username):
    """Validate a username; returns a list of error messages."""
    if not isinstance(username, str) or not username.strip():
        return ["Username is required"]

    value = username.strip()
    errors = []
    if len(value) < MIN_USERNAME_LENGTH:
        errors.append(f"Username must be at least {MIN_USERNAME_LENGTH} characters long")
    if len(value) > MAX_USERNAME_LENGTH:
        errors.append(f"Username must be at most {MAX_USERNAME_LENGTH} characters long")
    if not USERNAME_PATTERN.match(value):
        errors.append("Username may only contain letters, numbers, dots, hyphens and underscores")
    return errors


def validate_email_format(email):
    """Validate an email address; returns a list of error messages."""
    if not isinstance(email, str) or not email.strip():
        return ["Email is required"]

    value = email.strip()
    errors = []
    if len(value) > MAX_EMAIL_LENGTH:
        errors.append(f"Email must be at most {MAX_EMAIL_LENGTH} characters long")

    try:
        from email_validator import EmailNotValidError, validate_email as _validate_email

        try:
            _validate_email(value, check_deliverability=False)
        except EmailNotValidError:
            errors.append("Email format is invalid")
    except ImportError:  # pragma: no cover - email-validator is a declared dependency
        if not _FALLBACK_EMAIL_PATTERN.match(value):
            errors.append("Email format is invalid")

    return errors


def validate_password(password):
    """Validate a raw password; one message per failed rule."""
    if not isinstance(password, str) or not password:
        return ["Password is required"]

    errors = []
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(PASSWORD_RULES[0])
    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(f"Password must be at most {MAX_PASSWORD_LENGTH} characters long")
    if not any(char.isupper() for char in password):
        errors.append(PASSWORD_RULES[1])
    if not any(char.isdigit() for char in password):
        errors.append(PASSWORD_RULES[2])
    if not any(char in SPECIAL_CHARACTERS for char in password):
        errors.append(PASSWORD_RULES[3])
    return errors
