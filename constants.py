import os
from dotenv import load_dotenv

load_dotenv(".env")

API_KEY = os.getenv("YELP_API_KEY")
API_ENDPOINT = os.getenv("YELP_API_ENDPOINT")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")
