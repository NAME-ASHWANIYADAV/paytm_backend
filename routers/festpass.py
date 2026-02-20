"""FestPass API — college fest discovery and booking."""
from fastapi import APIRouter

from models import FeaturedFest, Fest, FestListResponse

router = APIRouter(prefix="/api/festpass", tags=["FestPass"])


@router.get("/featured", response_model=FeaturedFest)
async def get_featured():
    """Return the featured/trending fest."""
    return FeaturedFest(
        name="Techfest 2025",
        college="IIT Bombay",
        city="Mumbai",
        dates="Mar 14-16, 2025",
        trending="23 students from your campus going!",
    )


@router.get("/list", response_model=FestListResponse)
async def get_fests():
    """Return featured fest and all available fests."""
    featured = FeaturedFest(
        name="Techfest 2025",
        college="IIT Bombay",
        city="Mumbai",
        dates="Mar 14-16, 2025",
        trending="23 students from your campus going!",
    )

    fests = [
        Fest(
            name="Riviera 2025", college="VIT Vellore", city="Vellore",
            dates="Feb 28 - Mar 2", entry=300, travel=800, stay=400,
            gradient="from-primary/40 to-accent/20",
        ),
        Fest(
            name="Mood Indigo", college="IIT Bombay", city="Mumbai",
            dates="Mar 7-9", entry=500, travel=1200, stay=600,
            gradient="from-gold/40 to-gold/10",
        ),
        Fest(
            name="Oasis", college="BITS Pilani", city="Pilani",
            dates="Mar 21-24", entry=200, travel=600, stay=300,
            gradient="from-success/40 to-success/10",
        ),
        Fest(
            name="Saarang", college="IIT Madras", city="Chennai",
            dates="Apr 2-5", entry=400, travel=1000, stay=500,
            gradient="from-destructive/30 to-destructive/5",
        ),
    ]

    return FestListResponse(featured=featured, fests=fests)


@router.post("/book")
async def book_festpass(fest_name: str, group_size: int = 1):
    """Book a FestPass (mock endpoint)."""
    group_discount = group_size >= 5
    return {
        "fest": fest_name,
        "group_size": group_size,
        "group_discount_applied": group_discount,
        "discount_pct": 20 if group_discount else 0,
        "message": (
            f"🎉 FestPass booked for {fest_name}! "
            + ("Group discount of 20% applied!" if group_discount else "")
        ),
    }
