"""Dashboard API — stats, active trips, campus feed."""
from fastapi import APIRouter

from models import DashboardResponse, Stat, ActiveTrip, FeedItem

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Return dashboard data for the logged-in student."""
    stats = [
        Stat(label="Campus Credits", value="2,450", emoji="🪙", color="text-gold"),
        Stat(label="Digital Gold", value="₹127.50", emoji="🥇", color="text-gradient-gold"),
        Stat(label="Trips This Month", value="3", emoji="🚂", color="text-primary"),
        Stat(label="Savings", value="₹1,280", emoji="💰", color="text-success"),
    ]

    active_trips = [
        ActiveTrip(destination="Rishikesh", date="Feb 22-24", members=5, status="Booking", progress=60),
        ActiveTrip(destination="Lucknow", date="Feb 28", members=3, status="Planning", progress=30),
        ActiveTrip(destination="Jaipur", date="Mar 5-7", members=8, status="Confirmed", progress=100),
    ]

    feed = [
        FeedItem(text="Rahul paid ₹120 for Rishikesh trip", time="2m ago"),
        FeedItem(text="5 hostelmates going to Lucknow this weekend", time="15m ago"),
        FeedItem(text="New deal: 20% off at Campus Cafe", time="1h ago"),
        FeedItem(text="Tatkal window opens at 10:00 AM tomorrow", time="3h ago"),
    ]

    return DashboardResponse(
        greeting="Welcome back, Saksham",
        stats=stats,
        active_trips=active_trips,
        feed=feed,
    )
