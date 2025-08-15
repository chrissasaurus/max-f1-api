import os
from dotenv import load_dotenv

load_dotenv()

# Cache directory for FastF1
CACHE_DIR = os.getenv("CACHE_DIR", "./fastf1_cache")
