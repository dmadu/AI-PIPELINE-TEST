import os
from dotenv import load

load_dotenv = getattr(os, 'load_dotenv', None)
if load_dotenv:
    from dotenv import load_dotenv
    load_dotenv()

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
