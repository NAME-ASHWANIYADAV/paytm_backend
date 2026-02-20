"""GharWaapsi API — smart home route with concession, hostelmates, tatkal."""
from fastapi import APIRouter

from models import (
    RouteRequest, RouteResponse, Hostelmate,
    TatkalInfo, PapaPayRequest, PapaPayResponse,
)
from services.route_planner import calculate_route

router = APIRouter(prefix="/api/gharwaapsi", tags=["GharWaapsi"])


@router.post("/route", response_model=RouteResponse)
async def get_route(req: RouteRequest):
    """Calculate optimal multi-modal home route with student concession."""
    result = calculate_route(req.from_city, req.to_city)
    return RouteResponse(**result)


@router.get("/hostelmates", response_model=list[Hostelmate])
async def get_hostelmates():
    """Return hostelmates traveling on the same route."""
    return [
        Hostelmate(name="Rahul S.", initial="R", tag="Same train"),
        Hostelmate(name="Priya M.", initial="P", tag="Same train"),
        Hostelmate(name="Vikash K.", initial="V", tag="Same train"),
    ]


@router.get("/tatkal", response_model=TatkalInfo)
async def get_tatkal_info():
    """Return next Tatkal window information."""
    return TatkalInfo(
        next_window="10:00 AM",
        auto_fill_ready=True,
        alert_set=True,
    )


@router.post("/papa-pay", response_model=PapaPayResponse)
async def papa_pay(req: PapaPayRequest):
    """Generate UPI payment request for parent."""
    upi_id = req.parent_upi or "parent@paytm"
    upi_link = f"upi://pay?pa={upi_id}&pn=Paytm%20Campus%20OS&am={req.amount}&cu=INR&tn=Travel%20Fare%20Request"

    return PapaPayResponse(
        upi_link=upi_link,
        message=f"Payment request of ₹{req.amount} sent to {upi_id}",
        amount=req.amount,
    )
