from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
FLASK_ENV = os.getenv("FLASK_ENV", "dev") # Default to development if not set