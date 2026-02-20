"""Concession API — railway student concession calculator."""
from fastapi import APIRouter

from models import ConcessionRequest, ConcessionResult, StationsResponse
from services.concession_engine import calculate_concession, STATIONS

router = APIRouter(prefix="/api/concession", tags=["Concession"])


@router.get("/stations", response_model=StationsResponse)
async def get_stations():
    """Return list of available railway stations."""
    return StationsResponse(stations=STATIONS)


@router.post("/calculate", response_model=ConcessionResult)
async def calculate(req: ConcessionRequest):
    """Calculate student railway concession fare."""
    result = calculate_concession(
        from_station=req.from_station,
        to_station=req.to_station,
        travel_class=req.travel_class,
        category=req.category,
    )
    return ConcessionResult(**result)


@router.post("/bonafide")
async def generate_bonafide(req: ConcessionRequest):
    """Generate digital bonafide certificate data (PDF generation stub)."""
    concession = calculate_concession(
        req.from_station, req.to_station,
        req.travel_class, req.category,
    )

    return {
        "certificate": {
            "student_name": "Saksham Yason",
            "college": "Indian Institute of Technology, Lucknow",
            "enrollment_no": "2023BCS1042",
            "course": "B.Tech Computer Science",
            "year": "3rd Year",
            "from_station": req.from_station,
            "to_station": req.to_station,
            "travel_class": req.travel_class,
            "concession_type": req.category,
            "concession_fare": concession["concession_fare"],
            "valid_until": "2026-06-30",
            "verified_via": "DigiLocker + ABC (Academic Bank of Credits)",
            "verification_id": "DL-2026-STU-48291",
        },
        "message": "Digital bonafide certificate generated successfully!",
    }
