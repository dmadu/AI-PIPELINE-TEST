import os
import logging
from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, bcrypt, jwt, cors

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    cors.init_app(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Flask application initialized with {config_name} config")

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "healthy", "environment": config_name}, 200

    return app
