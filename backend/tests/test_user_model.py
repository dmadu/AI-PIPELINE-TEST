"""Tests for the User model and its password / lookup helpers."""

from datetime import datetime

import pytest

from app import create_app
from app.extensions import db
from app.models import User

RAW_PASSWORD = "Str0ng!Pass"


@pytest.fixture()
def model_app():
    """Create an application bound to the in-memory testing database."""
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def _create_user(username="Alice", email="  Alice@Example.COM ", password=RAW_PASSWORD):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def test_user_is_persisted(model_app):
    user = _create_user()

    assert user.id is not None
    assert user.username == "Alice"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_email_is_stored_lowercased_and_trimmed(model_app):
    user = _create_user(email="  MiXeD@Example.COM ")

    assert user.email == "mixed@example.com"


def test_set_and_check_password(model_app):
    user = _create_user()

    assert user.password_hash != RAW_PASSWORD
    assert user.check_password(RAW_PASSWORD) is True
    assert user.check_password("wrong-password") is False
    assert user.check_password("") is False


def test_set_password_rejects_empty_value(model_app):
    user = User(username="bob", email="bob@example.com")

    with pytest.raises(ValueError):
        user.set_password("")


def test_to_dict_exposes_only_public_fields(model_app):
    user = _create_user()

    payload = user.to_dict()

    assert set(payload.keys()) == {"id", "username", "email", "created_at"}
    assert "password_hash" not in payload
    assert "updated_at" not