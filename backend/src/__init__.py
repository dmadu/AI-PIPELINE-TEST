from flask import Flask
from flask_cors import CORS

def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app)

    @app.route('/health')
    def health_check():
        return {"status": "healthy"}, 200

    return app
