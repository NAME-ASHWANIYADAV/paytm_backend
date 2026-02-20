"""Indian Railway Concession Engine — fare calculation with student discounts."""
from __future__ import annotations

# ── Distance matrix (km) between major stations ───────────
# Approximate real Indian Railways distances
DISTANCE_MATRIX: dict[tuple[str, str], int] = {
    ("Lucknow", "Kanpur"): 82,
    ("Lucknow", "Allahabad"): 200,
    ("Lucknow", "Varanasi"): 300,
    ("Lucknow", "Delhi"): 511,
    ("Lucknow", "Mumbai"): 1380,
    ("Lucknow", "Patna"): 540,
    ("Lucknow", "Jaipur"): 580,
    ("Lucknow", "Haridwar"): 510,
    ("Kanpur", "Allahabad"): 193,
    ("Kanpur", "Varanasi"): 295,
    ("Kanpur", "Delhi"): 440,
    ("Kanpur", "Mumbai"): 1320,
    ("Kanpur", "Patna"): 610,
    ("Kanpur", "Jaipur"): 500,
    ("Kanpur", "Haridwar"): 520,
    ("Allahabad", "Varanasi"): 128,
    ("Allahabad", "Delhi"): 634,
    ("Allahabad", "Mumbai"): 1400,
    ("Allahabad", "Patna"): 415,
    ("Allahabad", "Jaipur"): 725,
    ("Allahabad", "Haridwar"): 740,
    ("Varanasi", "Delhi"): 780,
    ("Varanasi", "Mumbai"): 1500,
    ("Varanasi", "Patna"): 240,
    ("Varanasi", "Jaipur"): 870,
    ("Varanasi", "Haridwar"): 850,
    ("Delhi", "Mumbai"): 1384,
    ("Delhi", "Patna"): 1001,
    ("Delhi", "Jaipur"): 304,
    ("Delhi", "Haridwar"): 214,
    ("Mumbai", "Patna"): 1680,
    ("Mumbai", "Jaipur"): 1150,
    ("Mumbai", "Haridwar"): 1620,
    ("Patna", "Jaipur"): 960,
    ("Patna", "Haridwar"): 900,
    ("Jaipur", "Haridwar"): 475,
}

# All available stations
STATIONS = [
    "Lucknow", "Kanpur", "Allahabad", "Varanasi",
    "Delhi", "Mumbai", "Patna", "Jaipur", "Haridwar",
]

# ── Fare calculation (per km rates as per Indian Railways) ─
# These are approximate rates for 2025-2026
FARE_RATES = {
    "2S": {  # Second Sitting
        "base": 15,
        "per_km": 0.30,
    },
    "SL": {  # Sleeper
        "base": 20,
        "per_km": 0.45,
    },
}

# Concession percentages for students
CONCESSION_RATES = {
    "General": 50,   # 50% discount for general students
    "SC/ST": 75,     # 75% discount for SC/ST students
    "PH": 75,        # 75% discount for PH students
}


def get_distance(from_station: str, to_station: str) -> int | None:
    """Get distance between two stations (direction-agnostic)."""
    key1 = (from_station, to_station)
    key2 = (to_station, from_station)
    return DISTANCE_MATRIX.get(key1) or DISTANCE_MATRIX.get(key2)


def calculate_fare(distance_km: int, travel_class: str) -> int:
    """Calculate base fare from distance and class."""
    rates = FARE_RATES.get(travel_class, FARE_RATES["SL"])
    raw_fare = rates["base"] + (distance_km * rates["per_km"])
    # Round to nearest 5
    return int(round(raw_fare / 5) * 5)


def calculate_concession(
    from_station: str,
    to_station: str,
    travel_class: str,
    category: str,
) -> dict:
    """
    Calculate railway concession for a student.
    Returns full result including original fare, concession fare, savings, steps.
    """
    distance = get_distance(from_station, to_station)
    if distance is None:
        # Estimate based on generic distance
        distance = 300  # default fallback

    original_fare = calculate_fare(distance, travel_class)
    concession_pct = CONCESSION_RATES.get(category, 50)
    discount = int(original_fare * concession_pct / 100)
    concession_fare = original_fare - discount
    # Round to nearest 5
    concession_fare = int(round(concession_fare / 5) * 5)
    savings = original_fare - concession_fare

    steps = [
        f"1. Visit nearest railway counter with student ID",
        f"2. Show digital bonafide certificate (download from app)",
        f"3. Request concession ticket for {from_station} → {to_station}",
        f"4. Pay the concession fare of ₹{concession_fare}",
        f"5. Keep the receipt for verification on train",
    ]

    return {
        "from_station": from_station,
        "to_station": to_station,
        "travel_class": travel_class,
        "category": category,
        "original_fare": original_fare,
        "concession_fare": concession_fare,
        "savings": savings,
        "savings_pct": concession_pct,
        "verified_via": "DigiLocker + ABC",
        "steps": steps,
    }
