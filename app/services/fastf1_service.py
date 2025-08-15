import fastf1
from app.config import CACHE_DIR

# Enable caching
fastf1.Cache.enable_cache(CACHE_DIR)

def get_race_schedule(year: int):
    """Fetch race schedule for a given year."""
    schedule = fastf1.get_event_schedule(year)
    return schedule.to_dict(orient="records")  # return as list of dicts
