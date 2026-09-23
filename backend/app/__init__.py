from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate

def create_app(config_name=None):
    if config_name is None:
        config_name = 'default'
        
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy"}, 200
        
    return app
