from bson import ObjectId
from fastapi import APIRouter, Query
from app.services.standings import standings_service
from app.services.fast_f1.fastf1_service import (
    get_race_schedule,
    get_driver_standings,
    get_constructor_standings,
    get_race_results
)

from app.services.sync.sync_service import sync_season_data

from app.services.fast_f1.fastf1_service import (
    get_driver_standings as fastf1_get_driver_standings,
    get_constructor_standings as fastf1_get_constructor_standings,
    get_race_results as fastf1_get_race_results
)


router = APIRouter()



def serialize_doc(doc):
    """Recursively convert ObjectId to string."""
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc

@router.get("/schedule/{year}", summary="Get F1 Race Schedule")
def race_schedule(year: int):
    """Get the F1 race schedule for a given year."""
    return {"year": year, "schedule": get_race_schedule(year)}


@router.get("/driver-standings/{year}/{round_number}", summary="Get Driver Standings")
def driver_standings(year: int, round_number: int):
    """
    Get driver standings after a given round.
    `round_number` is the race round (1 = season opener, etc.)
    """
    return {"year": year, "round": round_number, "standings": fastf1_get_driver_standings(year, round_number)}


@router.get("/constructor-standings/{year}/{round_number}", summary="Get Constructor Standings")
def constructor_standings(year: int, round_number: int):
    """
    Get constructor standings after a given round.
    Calculated from driver points by team.
    """
    return {"year": year, "round": round_number, "standings": fastf1_get_constructor_standings(year, round_number)}


@router.get("/race-results/{year}/{round_number}", summary="Get Race Results")
def race_results(year: int, round_number: int):
    """Get official race results for a given round."""
    return {"year": year, "round": round_number, "results": fastf1_get_race_results(year, round_number)}

@router.post("/sync")
async def sync_data(year: int | None = None):
    return await sync_season_data(year)

@router.get("/wdc")
async def get_driver_standings(season: int | None = Query(None)):
    data = await standings_service.get_driver_standings(season)
    return serialize_doc(data)

@router.get("/wcc")
async def get_constructor_standings(season: int | None = Query(None)):
    data = await standings_service.get_constructor_standings(season)
    return serialize_doc(data)