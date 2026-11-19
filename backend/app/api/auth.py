"""Authentication endpoints: register, login and current user."""

from flask import Blueprint, current_app, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.user import User
from ..schemas.auth_schemas import validate_login_payload, validate_register_payload
from ..utils.errors import ApiError
from ..utils.responses import success

auth_bp = Blueprint("auth", __name__)

INVALID_CREDENTIALS_MESSAGE = "Invalid username/email or password"


@auth_bp.post("/register")
def register():
    """Create a new user account."""
    payload = validate_register_payload(request.get_json(silent=True))

    _assert_unique(payload["username"], payload["email"])

    user = User(username=payload["username"], email=payload["email"])
    user.set_password(payload["password"])

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.info("Registration conflict for username: %s", payload["username"])
        _assert_unique(payload["username"], payload["email"])
        raise ApiError("DUPLICATE_USERNAME", "This username is already taken.", 409)

    current_app.logger.info("User registered: %s", user.username)
    return success(user.to_dict(), 201)


@auth_bp.post("/login")
def login():
    """Authenticate a user by username or email and issue an access token."""
    payload = validate_login_payload(request.get_json(silent=True))

    user = User.find_by_identifier(payload["identifier"])
    if user is None or not user.check_password(payload["password"]):
        current_app.logger.info("Failed login attempt for: %s", payload["identifier"])
        raise ApiError("INVALID_CREDENTIALS", INVALID_CREDENTIALS_MESSAGE, 401)

    access_token = create_access_token(identity=str(user.id))
    current_app.logger.info("User logged in: %s", user.username)
    return success({"access_token": access_token, "user": user.to_dict()})


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the user owning the supplied Bearer token."""
    identity = get_jwt_identity()
    user = _resolve_user(identity)

    if user is None:
        current_app.logger.info("/auth/me unresolved identity: %s", identity)
        raise ApiError("NOT_FOUND", "User not found.", 404)

    current_app.logger.info("/auth/me resolved user: %s", user.username)
    return success(user.to_dict())


def _resolve_user(identity):
    """Convert a JWT identity into a User instance (or None)."""
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_id)


def _assert_unique(username, email):
    """Raise a 409 ApiError when the username or email is already taken."""
    if User.find_by_username(username) is not None:
        raise ApiError(
            "DUPLICATE_USERNAME",
            "This username is already taken.",
            409,
            {"username": "This username is already taken."},
        )
    if User.find_by_email(email) is not None:
        raise ApiError(
            "DUPLICATE_EMAIL",
            "This email is already registered.",
            409,
            {"email": "This email is already registered."},
        )
