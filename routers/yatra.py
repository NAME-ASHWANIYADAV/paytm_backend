"""Yatra API — AI trip planner with chat and trip plans."""
from fastapi import APIRouter

from models import (
    ChatRequest, ChatResponse, TripPlan,
    TransportOption, StayOption, Activity, GroupMember,
)
from services.ai_chat import get_ai_response

router = APIRouter(prefix="/api/yatra", tags=["Yatra"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """AI-powered trip planning chat endpoint."""
    reply, trip_generated = await get_ai_response(req.message, req.history)
    return ChatResponse(reply=reply, trip_generated=trip_generated)


@router.get("/chips")
async def get_chips():
    """Return suggestion chips for the chat."""
    return {"chips": ["Weekend Trip", "Tirth Yatra", "College Fest", "Home Visit"]}


@router.get("/plan", response_model=TripPlan)
async def get_trip_plan():
    """Return a sample generated trip plan (Rishikesh demo)."""
    return TripPlan(
        destination="Rishikesh, Uttarakhand",
        region="Uttarakhand",
        dates="Feb 22-24 (Sat-Mon)",
        member_count=5,
        price_per_person="₹1,850",
        transport=[
            TransportOption(mode="🚂 Train", route="Lucknow → Haridwar", time="8h 30m", price="₹380"),
            TransportOption(mode="🚌 Bus", route="Haridwar → Rishikesh", time="1h", price="₹60"),
        ],
        stays=[
            StayOption(name="Backpacker Hostel", rating=4.5, price="₹400/night", tag="Best Value"),
            StayOption(name="River View Camp", rating=4.2, price="₹600/night", tag="Scenic"),
        ],
        activities=[
            Activity(name="White Water Rafting", cost="₹500"),
            Activity(name="Laxman Jhula Visit", cost="Free"),
            Activity(name="Café hopping", cost="₹200"),
            Activity(name="Ganga Aarti", cost="Free"),
        ],
        budget_used=1850,
        budget_total=2000,
        members=[
            GroupMember(name="Saksham", status="paid"),
            GroupMember(name="Rahul", status="paid"),
            GroupMember(name="Priya", status="pending"),
            GroupMember(name="Amit", status="pending"),
            GroupMember(name="Neha", status="paid"),
        ],
    )
