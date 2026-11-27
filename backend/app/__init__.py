from flask import Flask
from flask_cors import CORS
from backend.app.config import config_by_name
from backend.app.extensions import db, migrate, bcrypt, jwt
from backend.app.models.user import User

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize CORS
    CORS(app)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200

    return app
