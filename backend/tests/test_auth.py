"""End-to-end tests for the authentication API.

Covers POST /api/v1/auth/register, POST /api/v1/auth/login and
GET /api/v1/auth/me through the Flask test client, asserting the documented
success payloads ({"data": ...}), the error envelope
({"error": {"code", "message", "fields"}}), status codes and bcrypt-hashed
storage of passwords.

Stories: S343 (registration), S344 (email/password validation),
S345 (secure password storage), S346 (login with username or email + JWT).
"""

import pytest

from app.models.user import User
from app.utils.validators import PASSWORD_RULES

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

VALID_PASSWORD = "StrongPass1!"
OTHER_VALID_PASSWORD = "AnotherPass2@"
GENERIC_LOGIN_ERROR = "Invalid username/email or password"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def register_payload(username="alice", email="alice@example.com",
                     password=VALID_PASSWORD, **overrides):
    """Build a registration body, allowing individual keys to be overridden."""
    payload = {"username": username, "email": email, "password": password}
    payload.update(overrides)
    return payload


def register(client, **kwargs):
    """POST a registration request built from :func:`register_payload`."""
    return client.post(REGISTER_URL, json=register_payload(**kwargs))


def login(client, identifier, password):
    """POST a login request with the single 'identifier' field."""
    return client.post(LOGIN_URL, json={"identifier": identifier,
                                        "password": password})


def assert_error_envelope(payload, expected_code=None):
    """Assert the documented error envelope shape and optionally its code."""
    assert isinstance(payload, dict), f"expected a JSON object, got {payload!r}"
    assert "error" in payload, f"missing error envelope: {payload!r}"
    error = payload["error"]
    assert isinstance(error, dict)
    assert isinstance(error.get("code"), str) and error["code"]
    assert isinstance(error.get("message"), str) and error["message"]
    if "fields" in error:
        assert isinstance(error["fields"], dict)
    if expected_code is not None:
        assert error["code"] == expected_code, f"unexpected error payload: {payload!r}"
    return error


def field_message(payload, field):
    """Return the (joined) validation message stored under error.fields[field]."""
    error = assert_error_envelope(payload, "VALIDATION_ERROR")
    assert "fields" in error, f"expected error.fields for '{field}': {payload!r}"
    assert field in error["fields"], f"expected error.fields.{field}: {payload!r}"
    value = error["fields"][field]
    if isinstance(value, (list, tuple)):
        message = " ".join(str(item) for item in value)
    else:
        message = str(value)
    assert message.strip(), f"empty message for field '{field}'"
    return message


def assert_user_payload(data, username, email):
    """Assert a serialised user matches User.to_dict() and leaks no hash."""
    assert isinstance(data, dict)
    assert data.get("id")
    assert data.get("username") == username
    assert data.get("email") == email.lower()
    assert data.get("created_at")
    assert "password_hash" not in data
    assert "password" not in data


def count_users(app, **filters):
    """Count User rows matching simple equality filters (case-insensitive)."""
    with app.app_context():
        query = User.query
        for key, value in filters.items():
            column = getattr(User, key)
            query = query.filter(column.ilike(value))
        return query.count()


def get_user(app, username):
    """Fetch a single User row by (case-insensitive) username."""
    with app.app_context():
        return User.query.filter(User.username.ilike(username)).first()


# --------------------------------------------------------------------------- #
# Fixtures local to the auth suite
# --------------------------------------------------------------------------- #
@pytest.fixture
def registered_user(client):
    """Register a known user through the API and return its credentials."""
    credentials = {
        "username": "alice",
        "email": "alice@example.com",
        "password": VALID_PASSWORD,
    }
    response = client.post(REGISTER_URL, json=credentials)
    assert response.status_code == 201, response.get_json()
    credentials["id"] = response.get_json()["data"]["id"]
    return credentials


@pytest.fixture
def access_token(client, registered_user):
    """Log the registered user in and return a valid access token."""
    response = login(client, registered_user["username"], registered_user["password"])
    assert response.status_code == 200, response.get_json()
    token = response.get_json()["data"]["access_token"]
    assert isinstance(token, str) and token
    return token


@pytest.fixture
def auth_headers(access_token):
    """Authorization header factory output for the registered user."""
    return {"Authorization": f"Bearer {access_token}"}


# --------------------------------------------------------------------------- #
# Registration - success path (S343)
# --------------------------------------------------------------------------- #
class TestRegistrationSuccess:

    def test_register_returns_201_with_data_envelope(self, client):
        response = register(client)

        assert response.status_code == 201
        payload = response.get_json()
        assert "data" in payload, payload
        assert "error" not in payload
        assert_user_payload(payload["data"], "alice", "alice@example.com")

    def test_register_persists_the_user_row(self, client, app):
        response = register(client, username="bob", email="Bob@Example.com")

        assert response.status_code == 201
        assert count_users(app, username="bob") == 1
        stored = get_user(app, "bob")
        assert stored is not None
        assert stored.email == "bob@example.com"

    def test_register_response_never_leaks_the_password(self, client):
        response = register(client, username="carol", email="carol@example.com")

        assert response.status_code == 201
        body = response.get_data(as_text=True)
        assert VALID_PASSWORD not in body
        assert "password_hash" not in body


# --------------------------------------------------------------------------- #
# Password storage (S345 / REQ-007)
# --------------------------------------------------------------------------- #
class TestPasswordHashing:

    def test_password_is_stored_hashed_not_in_plaintext(self, client, app):
        assert register(client, username="dave", email="dave@example.com").status_code == 201

        stored = get_user(app, "dave")
        assert stored is not None
        assert isinstance(stored.password_hash, str)
        assert stored.password_hash.strip() != ""
        assert stored.password_hash != VALID_PASSWORD
        assert VALID_PASSWORD not in stored.password_hash
        assert len(stored.password_hash) >= 50

    def test_check_password_matches_only_the_correct_password(self, client, app):
        assert register(client, username="erin", email="erin@example.com").status_code == 201

        stored = get_user(app, "erin")
        assert stored.check_password(VALID_PASSWORD) is True
        assert stored.check_password(OTHER_VALID_PASSWORD) is False


# --------------------------------------------------------------------------- #
# Email validation (S344 / REQ-005)
# --------------------------------------------------------------------------- #
class TestEmailValidation:

    @pytest.mark.parametrize("bad_email", [
        "plainaddress",            # missing @
        "alice@",                  # missing domain
        "@example.com",            # missing local part
        "alice@@example.com",      # double @
        "alice example@test.com",  # whitespace in local part
    ])
    def test_malformed_email_returns_400_validation_error(self, client, app, bad_email):
        response = client.post(REGISTER_URL, json=register_payload(email=bad_email))

        assert response.status_code == 400
        payload = response.get_json()
        message = field_message(payload, "email")
        assert "email" in message.lower()
        assert count_users(app, username="alice") == 0


# --------------------------------------------------------------------------- #
# Password validation (S344)
# --------------------------------------------------------------------------- #
class TestPasswordValidation:

    @pytest.mark.parametrize("password, keyword", [
        ("Sh1!a", "8"),            # shorter than 8 characters
        ("lowercase1!", "upper"),  # no uppercase letter
        ("NoDigitsHere!", "digit"),  # no digit
        ("NoSpecial123", "special"),  # no special character
    ])
    def test_password_rule_violation_returns_400(self, client, app, password, keyword):
        response = client.post(REGISTER_URL, json=register_payload(password=password))

        assert response.status_code == 400
        payload = response.get_json()
        message = field_message(payload, "password").lower()
        assert keyword in message, f"expected '{keyword}' in password message: {message!r}"
        assert count_users(app, username="alice") == 0

    def test_password_failing_several_rules_reports_every_failed_rule(self, client):
        # 'abc' fails length, uppercase, digit and special-character rules.
        response = client.post(REGISTER_URL, json=register_payload(password="abc"))

        assert response.status_code == 400
        message = field_message(response.get_json(), "password").lower()
        for keyword in ("8", "upper", "digit", "special"):
            assert keyword in message, (
                f"expected a message for the '{keyword}' rule, got: {message!r}"
            )

    def test_shared_password_rules_constant_defines_all_rules(self):
        assert PASSWORD_RULES, "PASSWORD_RULES must define the shared password policy"
        assert len(PASSWORD_RULES) >= 4


# --------------------------------------------------------------------------- #
# Missing / malformed request bodies
# --------------------------------------------------------------------------- #
class TestRegistrationBodyValidation:

    @pytest.mark.parametrize("missing_field", ["username", "email", "password"])
    def test_missing_required_field_returns_400(self, client, missing_field):
        payload = register_payload()
        payload.pop(missing_field)

        response = client.post(REGISTER_URL, json=payload)

        assert response.status_code == 400
        body = response.get_json()
        assert_error_envelope(body, "VALIDATION_ERROR")
        assert field_message(body, missing_field)

    @pytest.mark.parametrize("empty_field", ["username", "email", "password"])
    def test_empty_required_field_returns_400(self, client, empty_field):
        payload = register_payload(**{empty_field: ""})

        response = client.post(REGISTER_URL, json=payload)

        assert response.status_code == 400
        body = response.get_json()
        assert_error_envelope(body, "VALIDATION_ERROR")
        assert field_message(body, empty_field)

    def test_empty_json_object_returns_400(self, client):
        response = client.post(REGISTER_URL, json={})

        assert response.status_code == 400
        error = assert_error_envelope(response.get_json(), "VALIDATION_ERROR")
        assert error.get("fields")

    def test_non_json_body_returns_error_envelope_without_stack_trace(self, client):
        response = client.post(REGISTER_URL, data="not-json",
                               content_type="text/plain")

        assert response.status_code in (400, 415)
        assert_error_envelope(response.get_json())
        body = response.get_data(as_text=True)
        assert "Traceback" not in body

    def test_empty_body_returns_error_envelope(self, client):
        response = client.post(REGISTER_URL, data="",
                               content_type="application/json")

        assert response.status_code in (400, 415)
        assert_error_envelope(response.get_json())


# --------------------------------------------------------------------------- #
# Duplicate detection (S343 data-model rules)
# --------------------------------------------------------------------------- #
class TestDuplicateRegistration:

    def test_duplicate_username_returns_409(self, client, app, registered_user):
        response = register(client, username=registered_user["username"],
                           email="other@example.com")

        assert response.status_code == 409
        error = assert_error_envelope(response.get_json(), "DUPLICATE_USERNAME")
        assert error["message"]
        assert count_users(app, username=registered_user["username"]) == 1
        assert count_users(app, email="other@example.com") == 0

    def test_duplicate_username_is_case_insensitive(self, client, app, registered_user):
        response = register(client, username=registered_user["username"].upper(),
                           email="another@example.com")

        assert response.status_code == 409
        assert_error_envelope(response.get_json(), "DUPLICATE_USERNAME")
        assert count_users(app, username=registered_user["username"]) == 1

    def test_duplicate_email_returns_409(self, client, app, registered_user):
        response = register(client, username="different",
                           email=registered_user["email"])

        assert response.status_code == 409
        assert_error_envelope(response.get_json(), "DUPLICATE_EMAIL")
        assert count_users(app, email=registered_user["email"]) == 1
        assert count_users(app, username="different") == 0

    def test_duplicate_email_is_case_insensitive(self, client, app, registered_user):
        response = register(client, username="different2",
                           email=registered_user["email"].upper())

        assert response.status_code == 409
        assert_error_envelope(response.get_json(), "DUPLICATE_EMAIL")
        assert count_users(app, email=registered_user["email"]) == 1


# --------------------------------------------------------------------------- #
# Login (S346 / REQ-011)
# --------------------------------------------------------------------------- #
class TestLogin:

    def test_login_with_username_returns_token_and_user(self, client, registered_user):
        response = login(client, registered_user["username"], registered_user["password"])

        assert response.status_code == 200
        payload = response.get_json()
        assert "data" in payload, payload
        data = payload["data"]
        assert isinstance(data.get("access_token"), str)
        assert data["access_token"].strip() != ""
        assert_user_payload(data["user"], registered_user["username"],
                            registered_user["email"])
        assert data["user"]["id"] == registered_user["id"]

    def test_login_with_email_returns_token_and_user(self, client, registered_user):
        response = login(client, registered_user["email"], registered_user["password"])

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["access_token"]
        assert_user_payload(data["user"], registered_user["username"],
                            registered_user["email"])

    def test_login_with_differently_cased_email(self, client, registered_user):
        response = login(client, registered_user["email"].upper(),
                        registered_user["password"])

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["access_token"]
        assert data["user"]["email"] == registered_user["email"]

    def test_login_response_never_leaks_the_password(self, client, registered_user):
        response = login(client, registered_user["username"], registered_user["password"])

        body = response.get_data(as_text=True)
        assert VALID_PASSWORD not in body
        assert "password_hash" not in body

    def test_login_with_wrong_password_returns_generic_401(self, client, registered_user):
        response = login(client, registered_user["username"], "WrongPass9!")

        assert response.status_code == 401
        error = assert_error_envelope(response.get_json(), "INVALID_CREDENTIALS")
        assert error["message"] == GENERIC_LOGIN_ERROR
        assert "fields" not in error

    def test_login_with_unknown_identifier_returns_generic_401(self, client, registered_user):
        response = login(client, "nobody@example.com", VALID_PASSWORD)

        assert response.status_code == 401
        error = assert_error_envelope(response.get_json(), "INVALID_CREDENTIALS")
        assert error["message"] == GENERIC_LOGIN_ERROR
        assert "fields" not in error

    def test_login_errors_do_not_hint_at_user_existence(self, client, registered_user):
        wrong_password = login(client, registered_user["username"], "WrongPass9!")
        unknown_user = login(client, "ghost", VALID_PASSWORD)

        assert wrong_password.get_json() == unknown_user.get_json()

    @pytest.mark.parametrize("payload", [
        {},
        {"identifier": "alice"},
        {"password": VALID_PASSWORD},
        {"identifier": "", "password": ""},
    ])
    def test_login_with_missing_fields_returns_400(self, client, payload):
        response = client.post(LOGIN_URL, json=payload)

        assert response.status_code == 400
        error = assert_error_envelope(response.get_json(), "VALIDATION_ERROR")
        assert error.get("fields")


# --------------------------------------------------------------------------- #
# Protected route GET /api/v1/auth/me
# --------------------------------------------------------------------------- #
class TestCurrentUserEndpoint:

    def test_me_without_token_returns_401_token_missing(self, client):
        response = client.get(ME_URL)

        assert response.status_code == 401
        assert_error_envelope(response.get_json(), "TOKEN_MISSING")

    def test_me_with_malformed_bearer_token_returns_401_token_invalid(self, client):
        response = client.get(ME_URL, headers={"Authorization": "Bearer not-a-jwt"})

        assert response.status_code == 401
        assert_error_envelope(response.get_json(), "TOKEN_INVALID")

    def test_me_without_bearer_scheme_returns_401_token_invalid(self, client, access_token):
        response = client.get(ME_URL, headers={"Authorization": access_token})

        assert response.status_code == 401
        assert_error_envelope(response.get_json(), "TOKEN_INVALID")

    def test_me_with_valid_token_returns_the_current_user(self, client, auth_headers,
                                                          registered_user):
        response = client.get(ME_URL, headers=auth_headers)

        assert response.status_code == 200
        payload = response.get_json()
        assert "data" in payload, payload
        assert_user_payload(payload["data"], registered_user["username"],
                            registered_user["email"])
        assert payload["data"]["id"] == registered_user["id"]

    def test_me_matches_the_user_returned_by_login(self, client, registered_user):
        login_response = login(client, registered_user["email"], registered_user["password"])
        data = login_response.get_json()["data"]
        headers = {"Authorization": f"Bearer {data['access_token']}"}

        me_response = client.get(ME_URL, headers=headers)

        assert me_response.status_code == 200
        assert me_response.get_json()["data"] == data["user"]
