"""User model.

This module owns the single entity of the system (table ``users``) and is the
only place in the backend where Flask-Bcrypt is used.  Passwords are never
stored in clear text and are never exposed through :meth:`User.to_dict`.
"""

from datetime import datetime, timezone

from sqlalchemy import func, text
from sqlalchemy.orm import validates

from app.extensions import bcrypt, db


def utcnow():
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class User(db.Model):
    """Application user.

    Columns follow the approved data model: ``id``, ``username``, ``email``,
    ``password_hash``, ``created_at`` and ``updated_at``.  Emails are always
    persisted lowercased/trimmed while usernames are stored exactly as given;
    case-insensitive lookups are provided by the ``find_by_*`` helpers which
    rely on ``lower()`` functional indexes.
    """

    __tablename__ = "users"

    __table_args__ = (
        db.UniqueConstraint("username", name="uq_users_username"),
        db.UniqueConstraint("email", name="uq_users_email"),
        db.Index("ix_users_username_lower", text("lower(username)")),
        db.Index("ix_users_email_lower", text("lower(email)")),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    @validates("email")
    def _normalise_email(self, key, value):
        """Normalise the email to a trimmed, lowercased value on assignment."""
        if value is None:
            return value
        return str(value).strip().lower()

    @validates("username")
    def _normalise_username(self, key, value):
        """Trim surrounding whitespace; casing is preserved as given."""
        if value is None:
            return value
        return str(value).strip()

    def set_password(self, raw):
        """Hash ``raw`` with bcrypt and store it in ``password_hash``."""
        if not raw or not isinstance(raw, str):
            raise ValueError("Password must be a non-empty string.")
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw):
        """Return True when ``raw`` matches the stored bcrypt hash."""
        if not raw or not isinstance(raw, str) or not self.password_hash:
            return False
        return bool(bcrypt.check_password_hash(self.password_hash, raw))

    def to_dict(self):
        """Return the safe public representation of the user.

        Only ``id``, ``username``, ``email`` and ``created_at`` are exposed;
        ``password_hash`` and ``updated_at`` are never included.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self._iso_created_at(),
        }

    def _iso_created_at(self):
        """Serialise ``created_at`` as an ISO-8601 UTC string (or None)."""
        value = self.created_at
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()

    @classmethod
    def find_by_email(cls, email):
        """Return the user whose email matches ``email``, ignoring case."""
        if not email or not isinstance(email, str):
            return None
        needle = email.strip()
        if not needle:
            return None
        stmt = db.select(cls).where(func.lower(cls.email) == func.lower(needle))
        return db.session.execute(stmt).scalars().first()

    @classmethod
    def find_by_username(cls, username):
        """Return the user whose username matches ``username``, ignoring case."""
        if not username or not isinstance(username, str):
            return None
        needle = username.strip()
        if not needle:
            return None
        stmt = db.select(cls).where(func.lower(cls.username) == func.lower(needle))
        return db.session.execute(stmt).scalars().first()

    @classmethod
    def find_by_identifier(cls, identifier):
        """Return the user matching ``identifier`` as email or username."""
        if not identifier or not isinstance(identifier, str):
            return None
        needle = identifier.strip()
        if not needle:
            return None
        lowered = func.lower(needle)
        stmt = db.select(cls).where(
            db.or_(
                func.lower(cls.email) == lowered,
                func.lower(cls.username) == lowered,
            )
        )
        return db.session.execute(stmt).scalars().first()

    def __repr__(self):
        """Return a developer friendly representation (no secrets)."""
        return f"<User id={self.id} username={self.username!r}>"
