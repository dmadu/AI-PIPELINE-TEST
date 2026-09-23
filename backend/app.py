import os
from dotenv import load
from src import create_app

load.load_dotenv() if hasattr(load, 'load_dotenv') else None

from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
