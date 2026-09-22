import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    # Configuration selection
    env = config_name or os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif env == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'database': str(e)}, 500

    return app
