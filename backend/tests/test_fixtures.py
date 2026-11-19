"""Tests proving the shared fixtures give each test an isolated database.

The two tests below run in file order: the first inserts a user, the second
asserts the table is empty again, so no state leaks between tests.
"""

from app.models.user import User


def test_db_fixture_persists_user_within_a_single_test(db):
    user = User(username="isolation_user", email="isolation@example.com")
    user.set_password("Str0ng!Pass")
    db.session.add(user)
    db.session.commit()

    assert db.session.query(User).count() == 1


def test_db_fixture_leaves_no_rows_for_the_next_test(db):
    assert db.session.query(User).count() == 0


def test_app_fixture_uses_sqlite_in_memory_testing_config(app):
    assert app.config["TESTING"] is True
    assert "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]
    assert ":memory:" in app.config["SQLALCHEMY_DATABASE_URI"]
