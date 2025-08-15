from fastapi import APIRouter
from app.services.fastf1_service import get_race_schedule

router = APIRouter()

@router.get("/schedule/{year}")
def race_schedule(year: int):
    """Get the F1 race schedule for a given year."""
    try:
        data = get_race_schedule(year)
        return {"year": year, "schedule": data}
    except Exception as e:
        return {"error": str(e)}
