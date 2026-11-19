"""Request parsing and validation schemas for the REST API.

The modules in this package are pure helpers: they receive the decoded request
body, delegate every field rule to :mod:`app.utils.validators` and either raise
an :class:`~app.utils.errors.ApiError` or return a clean dict of normalised
values. They never touch Flask's request object or the database.
"""

from app.schemas.auth_schemas import parse_login_payload, parse_register_payload

__all__ = ["parse_login_payload", "parse_register_payload"]
