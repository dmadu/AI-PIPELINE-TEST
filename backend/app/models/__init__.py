"""SQLAlchemy models package.

Importing this package registers every model class with the shared
``db.metadata`` so that Alembic autogenerate and ``db.create_all()`` can see
the full schema.
"""

from app.models.user import User

__all__ = ["User"]
