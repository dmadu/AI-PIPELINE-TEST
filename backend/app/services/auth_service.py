import re
from flask_bcrypt import Bcrypt
from app.models.user import User
from app import db

bcrypt = Bcrypt()

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return bool(re.match(pattern, email))
