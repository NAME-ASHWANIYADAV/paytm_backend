"""Multi-modal Route Planner — smart home route for students."""
from __future__ import annotations

from services.concession_engine import get_distance, calculate_fare, CONCESSION_RATES

# ── Auto/Cab fare estimation (per city) ────────────────────
AUTO_BASE_FARE = 30  # base fare in ₹
AUTO_PER_KM = 12     # ₹ per km for auto

# Campus bus fare (fixed)
CAMPUS_BUS_FARE = 10

# Last-mile distance estimates from station to home (km)
LAST_MILE_KM = {
    "Lucknow": 5, "Kanpur": 4, "Allahabad": 6, "Varanasi": 5,
    "Delhi": 8, "Mumbai": 10, "Patna": 6, "Jaipur": 5, "Haridwar": 3,
}

# Train duration estimates (hours)
TRAIN_DURATION = {
    82: "1h 30m", 200: "3h 30m", 300: "5h", 440: "6h 30m",
    511: "7h 30m", 540: "8h", 580: "8h 30m", 510: "7h 45m",
}


def _estimate_duration(distance_km: int) -> str:
    """Estimate train duration from distance."""
    # Find closest known duration
    closest = min(TRAIN_DURATION.keys(), key=lambda k: abs(k - distance_km))
    if abs(closest - distance_km) < 50:
        return TRAIN_DURATION[closest]
    # Estimate at ~60 km/h average
    hours = distance_km / 65
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m:02d}m"


def _estimate_auto_fare(city: str) -> int:
    """Estimate auto fare for last mile in a city."""
    km = LAST_MILE_KM.get(city, 5)
    fare = AUTO_BASE_FARE + (km * AUTO_PER_KM)
    return int(round(fare / 5) * 5)  # Round to nearest 5


def calculate_route(
    from_city: str,
    to_city: str,
    category: str = "General",
) -> dict:
    """
    Calculate multi-modal route: Campus Bus → Train → Auto.
    Applies student concession to train fare.
    """
    # Step 1: Campus bus to station
    bus_fare = CAMPUS_BUS_FARE

    # Step 2: Train fare with concession
    distance = get_distance(from_city, to_city)
    if distance is None:
        distance = 300  # fallback

    original_train_fare = calculate_fare(distance, "SL")
    concession_pct = CONCESSION_RATES.get(category, 50)
    discount = int(original_train_fare * concession_pct / 100)
    concession_train_fare = original_train_fare - discount
    concession_train_fare = int(round(concession_train_fare / 5) * 5)
    duration = _estimate_duration(distance)

    # Step 3: Auto from destination station to home
    auto_fare = _estimate_auto_fare(to_city)

    # Build route steps
    steps = [
        {
            "icon": "🏫",
            "from_location": "Hostel",
            "transport": "🚌 Campus Bus",
            "to_location": "Railway Station",
            "price": f"₹{bus_fare}",
            "detail": "Every 30 min from Main Gate",
            "badge": False,
        },
        {
            "icon": "🚂",
            "from_location": f"Train: {from_city} → {to_city}",
            "transport": "Sleeper Class",
            "to_location": "",
            "price": f"₹{concession_train_fare}",
            "detail": f"{concession_pct}% Student Concession Applied!",
            "badge": True,
        },
        {
            "icon": "🛺",
            "from_location": "Auto from Station",
            "transport": "",
            "to_location": "Home",
            "price": f"₹{auto_fare}",
            "detail": "Estimated fare via Ola/Uber",
            "badge": False,
        },
    ]

    # Totals
    total_discounted = bus_fare + concession_train_fare + auto_fare
    total_original = bus_fare + original_train_fare + auto_fare
    savings = total_original - total_discounted

    return {
        "steps": steps,
        "total_original": total_original,
        "total_discounted": total_discounted,
        "savings": savings,
        "savings_text": f"You save ₹{savings} with student concession! 🎉",
    }
