"""Shared backend utilities: error types, response envelopes and validators.

This package is the single place where the API response/error envelope and the
input validation rules are defined.  Everything exported here is safe to import
from blueprints, schemas and tests.
"""

from app.utils.errors import ApiError, register_error_handlers
from app.utils.responses import error_response, success
from app.utils.validators import (
    PASSWORD_RULES,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    validate_email_format,
    validate_password,
    validate_username,
)

__all__ = [
    "ApiError",
    "register_error_handlers",
    "success",
    "error_response",
    "PASSWORD_RULES",
    "USERNAME_MIN_LENGTH",
    "USERNAME_MAX_LENGTH",
    "validate_email_format",
    "validate_username",
    "validate_password",
]
