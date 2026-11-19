"""User model - the only place where bcrypt hashing is performed."""

from datetime import datetime, timezone

from sqlalchemy import func

from ..extensions import bcrypt, db


def _utcnow():
    """Return the current UTC time (naive, stored as UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    """Application user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    def set_password(self, raw_password):
        """Hash and store the given plain-text password."""
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        """Return True when the plain-text password matches the stored hash."""
        if not self.password_hash or raw_password is None:
            return False
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        """Public representation of the user - never exposes password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def find_by_username(cls, username):
        """Case-insensitive username lookup."""
        if not username:
            return None
        stmt = db.select(cls).where(func.lower(cls.username) == username.strip().lower())
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def find_by_email(cls, email):
        """Case-insensitive email lookup."""
        if not email:
            return None
        stmt = db.select(cls).where(func.lower(cls.email) == email.strip().lower())
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def find_by_identifier(cls, identifier):
        """Look a user up by either username or email."""
        if not identifier:
            return None
        value = identifier.strip().lower()
        stmt = db.select(cls).where(
            db.or_(func.lower(cls.username) == value, func.lower(cls.email) == value)
        )
        return db.session.execute(stmt).scalars().first()

    def __repr__(self):  # pragma: no cover - debugging helper
        return f"<User {self.id} {self.username}>"
