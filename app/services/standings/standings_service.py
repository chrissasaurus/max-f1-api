# app/services/standings_service.py
from datetime import datetime
from app.utils.db import db


async def get_driver_standings(year: int | None = None):
    """
    Get World Drivers' Championship standings for a given year.
    Defaults to the current year if not provided.
    """
    if year is None:
        year = datetime.utcnow().year

    standings = await db.wdc_points.find({"year": year}).sort("position", 1).to_list(length=None)
    return {
        "year": year,
        "standings": standings
    }


async def get_constructor_standings(year: int | None = None):
    """
    Get World Constructors' Championship standings for a given year.
    Defaults to the current year if not provided.
    """
    if year is None:
        year = datetime.utcnow().year

    standings = await db.wcc_points.find({"year": year}).sort("position", 1).to_list(length=None)
    return {
        "year": year,
        "standings": standings
    }
