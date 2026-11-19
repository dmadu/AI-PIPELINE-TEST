"""Shared Flask extension singletons.

Importing the extensions from this module (instead of creating them inside the
application factory) keeps the import graph flat and avoids circular imports
between models, blueprints and the factory itself.
"""

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()

__all__ = ["db", "migrate", "bcrypt", "jwt", "cors"]
