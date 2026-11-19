"""User model - the only place bcrypt hashing is performed."""

from datetime import datetime, timezone

from sqlalchemy.orm import validates

from ..extensions import bcrypt, db


def _utcnow():
    """Return a naive UTC timestamp (consistent across SQLite and PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    """Registered application user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    @validates("email")
    def _normalise_email(self, _key, value):
        """Emails are always stored lowercased."""
        return value.strip().lower() if isinstance(value, str) else value

    @validates("username")
    def _strip_username(self, _key, value):
        return value.strip() if isinstance(value, str) else value

    def set_password(self, raw_password):
        """Hash and store the given raw password."""
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        """Return True when the raw password matches the stored hash."""
        if not raw_password or not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        """Public representation - never includes the password hash."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):  # pragma: no cover - debugging helper
        return f"<User {self.id} {self.username}>"
