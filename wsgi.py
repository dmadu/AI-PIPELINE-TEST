import os
from src import create_app
from src.extensions import db

app = create_app(os.getenv("FLASK_ENV", "default"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
