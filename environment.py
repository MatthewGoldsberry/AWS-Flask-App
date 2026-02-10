"""Keys for the Flask App."""

import os

from dotenv import load_dotenv

load_dotenv()

if not (db := os.getenv("DATABASE")):
    raise OSError("'DATABASE' environment variable must be set in a .env file.")  # noqa: EM101, TRY003
DATABASE: str = db

if not (key := os.getenv("FLASK_SECRET_KEY")):
    raise OSError("'FLASK_SECRET_KEY' environment variable must be set in a .env file.")  # noqa: EM101, TRY003
FLASK_SECRET_KEY = key

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
