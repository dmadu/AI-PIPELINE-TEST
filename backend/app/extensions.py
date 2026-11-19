"""Uninitialised extension singletons shared across the application.

Every module imports its extensions from here so that the application factory remains the only
place where ``init_app`` is called and no circular imports are introduced.
"""

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

__all__ = ["db", "migrate", "bcrypt", "jwt", "cors"]

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
