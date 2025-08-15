import fastf1
from datetime import datetime
from app.config import CACHE_DIR
from app.utils.db import db

fastf1.Cache.enable_cache(CACHE_DIR)


async def sync_season_data(year: int | None = None):
    """
    Syncs the given year's F1 season data (or current year if not specified).
    Stores:
    - Driver details
    - Team details
    - Season calendar
    - Race results
    - World Drivers Championship (WDC) standings
    - World Constructors Championship (WCC) standings
    - Last sync timestamp
    """

    # Default to current year if no year provided
    if year is None:
        year = datetime.utcnow().year

    # Fetch the event schedule
    schedule = fastf1.get_event_schedule(year)
    today = datetime.utcnow()

    driver_points = {}
    constructor_points = {}

    completed_races = schedule[schedule['EventDate'] < today]

    # Clear existing data for that year before fresh sync
    await db.drivers.delete_many({"year": year})
    await db.teams.delete_many({"year": year})
    await db.calendar.delete_many({"year": year})
    await db.wdc_points.delete_many({"year": year})
    await db.wcc_points.delete_many({"year": year})
    await db.race_results.delete_many({"year": year})

    # Save the full season calendar
    calendar_docs = [
        {
            "year": year,
            "round": int(race['RoundNumber']),
            "name": race['EventName'],
            "date": race['EventDate'].to_pydatetime(),
            "location": race['Location'],
            "country": race['Country']
        }
        for _, race in schedule.iterrows()
    ]
    if calendar_docs:
        await db.calendar.insert_many(calendar_docs)

    # Keep track to avoid duplicate inserts
    seen_drivers = set()
    seen_teams = set()

    # Process completed races
    for _, race in completed_races.iterrows():
        round_number = int(race['RoundNumber'])

        # Skip pre-season testing
        if "test" in race['EventName'].lower():
            continue

        try:
            session = fastf1.get_session(year, round_number, 'R')
            session.load()
        except Exception as e:
            print(f"Skipping round {round_number} ({race['EventName']}): {e}")
            continue

        race_result_docs = []

        for _, row in session.results.iterrows():
            driver_code = row['Abbreviation']
            team_name = row['TeamName']
            points = row['Points']
            position = int(row['Position'])

            # Update points tally
            driver_points[driver_code] = driver_points.get(driver_code, 0) + points
            constructor_points[team_name] = constructor_points.get(team_name, 0) + points

            # Store driver details if not already added
            if driver_code not in seen_drivers:
                driver_info = session.get_driver(driver_code)
                await db.drivers.insert_one({
                    "year": year,
                    "code": driver_code,
                    "full_name": driver_info.FullName,
                    "first_name": driver_info.FirstName,
                    "last_name": driver_info.LastName,
                    "number": driver_info.DriverNumber,
                    "team": team_name
                })
                seen_drivers.add(driver_code)

            # Store team details if not already added
            if team_name not in seen_teams:
                await db.teams.insert_one({
                    "year": year,
                    "name": team_name
                })
                seen_teams.add(team_name)

            # Add race result entry
            race_result_docs.append({
                "year": year,
                "round": round_number,
                "driver": driver_code,
                "team": team_name,
                "position": position,
                "points": points,
                "time": str(row['Time']) if row['Time'] is not None else None
            })

        if race_result_docs:
            await db.race_results.insert_many(race_result_docs)

    # Calculate & save WDC standings
    wdc_docs = [
        {
            "year": year,
            "driver": driver,
            "points": points,
            "position": i
        }
        for i, (driver, points) in enumerate(
            sorted(driver_points.items(), key=lambda x: x[1], reverse=True), start=1
        )
    ]
    if wdc_docs:
        await db.wdc_points.insert_many(wdc_docs)

    # Calculate & save WCC standings
    wcc_docs = [
        {
            "year": year,
            "team": team,
            "points": points,
            "position": i
        }
        for i, (team, points) in enumerate(
            sorted(constructor_points.items(), key=lambda x: x[1], reverse=True), start=1
        )
    ]
    if wcc_docs:
        await db.wcc_points.insert_many(wcc_docs)

    # Update last sync timestamp
    await db.last_sync.update_one(
        {"year": year},
        {"$set": {
            "last_sync": datetime.utcnow(),
            "completed_races": len(completed_races)
        }},
        upsert=True
    )

    return {
        "year": year,
        "completed_races": len(completed_races),
        "drivers_synced": len(driver_points),
        "constructors_synced": len(constructor_points)
    }
