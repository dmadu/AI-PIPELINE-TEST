"""Authentication endpoints (/api/v1/auth)."""

from flask import Blueprint, current_app, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.user import User
from ..schemas.auth_schemas import parse_register_request
from ..utils.errors import ApiError
from ..utils.responses import success

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

DUPLICATE_USERNAME_CODE = "DUPLICATE_USERNAME"
DUPLICATE_EMAIL_CODE = "DUPLICATE_EMAIL"
DUPLICATE_USERNAME_MESSAGE = "Username is already taken"
DUPLICATE_EMAIL_MESSAGE = "Email is already registered"
DUPLICATE_GENERIC_MESSAGE = "An account with these details already exists"


def _duplicate_error(field):
    """Build the 409 ApiError for the offending field (``username``/``email``)."""
    if field == "email":
        return ApiError(
            DUPLICATE_EMAIL_CODE,
            DUPLICATE_EMAIL_MESSAGE,
            409,
            {"email": DUPLICATE_EMAIL_MESSAGE},
        )
    return ApiError(
        DUPLICATE_USERNAME_CODE,
        DUPLICATE_USERNAME_MESSAGE,
        409,
        {"username": DUPLICATE_USERNAME_MESSAGE},
    )


def _username_taken(username):
    """Case-insensitive lookup of an existing username."""
    stmt = db.select(User.id).where(func.lower(User.username) == username.lower())
    return db.session.execute(stmt).first() is not None


def _email_taken(email):
    """Case-insensitive lookup of an existing email (emails are stored lowercased)."""
    stmt = db.select(User.id).where(func.lower(User.email) == email.lower())
    return db.session.execute(stmt).first() is not None


def _duplicate_error_from_integrity(error):
    """Map a unique-constraint IntegrityError onto the matching 409 ApiError.

    The insert can still fail when two concurrent requests pass the duplicate
    lookup at the same time, so the driver message is inspected to decide which
    column collided. When it cannot be determined we fall back to a generic
    duplicate error using the DUPLICATE_US