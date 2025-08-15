import fastf1
from app.config import CACHE_DIR

# Enable caching
fastf1.Cache.enable_cache(CACHE_DIR)

def get_race_schedule(year: int):
    """Fetch race schedule for a given year."""
    schedule = fastf1.get_event_schedule(year)
    return schedule.to_dict(orient="records")


def get_driver_standings(year: int, round_number: int):
    """Fetch driver standings after a given round."""
    session = fastf1.get_session(year, round_number, 'R')
    session.load()
    standings = session.results[['Abbreviation', 'DriverNumber', 'Position', 'Points']]
    return standings.to_dict(orient="records")


def get_constructor_standings(year: int, round_number: int):
    """Fetch constructor standings after a given round."""
    session = fastf1.get_session(year, round_number, 'R')
    session.load()
    # No direct constructor standings in FastF1, so we sum driver points by team
    standings = session.results.groupby('TeamName')['Points'].sum().reset_index()
    standings['Position'] = standings['Points'].rank(ascending=False, method='min').astype(int)
    return standings.sort_values('Position').to_dict(orient="records")


def get_race_results(year: int, round_number: int):
    """Fetch race results for a given round."""
    session = fastf1.get_session(year, round_number, 'R')
    session.load()
    results = session.results[['Abbreviation', 'Position', 'Time', 'Points']]
    return results.to_dict(orient="records")
