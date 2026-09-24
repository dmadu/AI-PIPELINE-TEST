import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import config_map

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    
    # Load configuration
    config_class = config_map.get(config_name, config_map['default'])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'database': 'configured'}, 200

    return app
