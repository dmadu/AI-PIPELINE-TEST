"""Tests for the shared validation helpers in ``app.utils.validators``."""

import pytest

from app.utils import validators
from app.utils.errors import ApiError

VALID_PASSWORD = "Str0ng!Pass"
VALID_USERNAME = "john_doe"


def _normalise(result):
    """Turn a validator return value into a flat list of error messages."""
    if result is None:
        return []
    if isinstance(result, bool):
        return [] if result else ["invalid"]
    if isinstance(result, str):
        return [result] if result else []
    if isinstance(result, (list, tuple, set)):
        items = list(result)
        if len(items) == 2 and isinstance(items[0], bool):
            is_valid, detail = items
            if is_valid:
                return []
            if detail is None:
                return ["invalid"]
            if isinstance(detail, (list, tuple, set)):
                return [str(item) for item in detail]
            return [str(detail)]
        return [str(item) for item in items]
    return [str(result)]


def _errors(validator, value):
    """Run ``validator`` against ``value`` and return its error messages.

    The helper keeps the assertions focused on behaviour (which rules fail and
    how many messages are produced) rather than on the exact signalling style
    used by the implementation, which may return a message, a list of messages,
    a boolean/tuple pair or raise ``ApiError``.
    """
    try:
        result = validator(value)
    except ApiError as exc:
        messages = []
        for field_message in (getattr(exc, "fields", None) or {}).values():
            if isinstance(field_message, (list, tuple, set)):
                messages.extend(str(item) for item in field_message)
            else:
                messages.append(str(field_message))
        return messages or [str(getattr(exc, "message", exc))]
    return _normalise(result)


# --------------------------------------------------------------------------- #
# Email
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "first.last@example.co.uk",
        "user+tag@example.com",
    ],
)
def test_validate_email_format_valid_email_returns_no_errors(email):
    assert _errors(validators.validate_email_format, email) == []


@pytest.mark.parametrize(
    "email",
    [
        "",
        "   ",
        "not-an-email",
        "user@",
        "@example.com",
        "user@@example.com",
        "user example@example.com",
    ],
)
def test_validate_email_format_malformed_email_returns_error(email):
    assert len(_errors(validators.validate_email_format, email)) >= 1


# --------------------------------------------------------------------------- #
# Username
# --------------------------------------------------------------------------- #


def test_validate_username_valid_username_returns_no_errors():
    assert _errors(validators.validate_username, VALID_USERNAME) == []


def test_validate_username_too_short_returns_error():
    assert len(_errors(validators.validate_username, "a")) >= 1


def test_validate_username_too_long_returns_error():
    assert len(_errors(validators.validate_username, "a" * 101)) >= 1


@pytest.mark.parametrize("username", ["invalid user", "bad!name", "user@name", ""])
def test_validate_username_invalid_characters_returns_error(username):
    assert len(_errors(validators.validate_username, username)) >= 1


# --------------------------------------------------------------------------- #
# Password
# --------------------------------------------------------------------------- #


def test_validate_password_compliant_password_returns_no_errors():
    assert _errors(validators.validate_password, VALID_PASSWORD) == []


def test_validate_password_too_short_reports_single_message():
    assert len(_errors(validators.validate_password, "Ab1!")) == 1


def test_validate_password_without_uppercase_reports_single_message():
    assert len(_errors(validators.validate_password, "abcdefg1!")) == 1


def test_validate_password_without_digit_reports_single_message():
    assert len(_errors(validators.validate_password, "Abcdefgh!")) == 1


def test_validate_password_without_special_character_reports_single_message():
    assert len(_errors(validators.validate_password, "Abcdefg1")) == 1


def test_validate_password_failing_every_rule_reports_one_message_per_rule():
    errors = _errors(validators.validate_password, "abc")

    assert len(errors) == 4
    assert len(set(errors)) == 4

    individual_messages = set()
    for password in ("Ab1!", "abcdefg1!", "Abcdefgh!", "Abcdefg1"):
        individual_messages.update(_errors(validators.validate_password, password))
    assert individual_messages == set(errors)


def test_password_rules_constant_is_exposed_and_not_empty():
    assert hasattr(validators, "PASSWORD_RULES")
    assert len(validators.PASSWORD_RULES) > 0
