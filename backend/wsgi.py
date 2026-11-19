"""WSGI entrypoint.

Run with ``gunicorn wsgi:app`` from the ``backend/`` directory.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":  # pragma: no cover - local convenience runner.
    app.run(host="0.0.0.0", port=5000)
