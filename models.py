"""Pydantic models for Paytm Campus OS API."""
from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


# ── Dashboard ──────────────────────────────────────────────
class Stat(BaseModel):
    label: str
    value: str
    emoji: str
    color: str


class ActiveTrip(BaseModel):
    destination: str
    date: str
    members: int
    status: str
    progress: int


class FeedItem(BaseModel):
    text: str
    time: str


class DashboardResponse(BaseModel):
    greeting: str
    stats: list[Stat]
    active_trips: list[ActiveTrip]
    feed: list[FeedItem]


# ── Yatra (Trip Planner) ──────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    trip_generated: bool = False


class TransportOption(BaseModel):
    mode: str
    route: str
    time: str
    price: str


class StayOption(BaseModel):
    name: str
    rating: float
    price: str
    tag: str


class Activity(BaseModel):
    name: str
    cost: str


class GroupMember(BaseModel):
    name: str
    status: str  # "paid" | "pending"


class TripPlan(BaseModel):
    destination: str
    region: str
    dates: str
    member_count: int
    price_per_person: str
    transport: list[TransportOption]
    stays: list[StayOption]
    activities: list[Activity]
    budget_used: int
    budget_total: int
    members: list[GroupMember]


# ── GharWaapsi ─────────────────────────────────────────────
class RouteRequest(BaseModel):
    from_city: str
    to_city: str


class RouteStep(BaseModel):
    icon: str
    from_location: str  # 'from' is reserved in Python
    transport: str
    to_location: str
    price: str
    detail: str
    badge: bool = False


class Hostelmate(BaseModel):
    name: str
    initial: str
    tag: str = "Same train"


class TatkalInfo(BaseModel):
    next_window: str
    auto_fill_ready: bool
    alert_set: bool


class RouteResponse(BaseModel):
    steps: list[RouteStep]
    total_original: int
    total_discounted: int
    savings: int
    savings_text: str


class PapaPayRequest(BaseModel):
    amount: int
    parent_upi: str = ""


class PapaPayResponse(BaseModel):
    upi_link: str
    message: str
    amount: int


# ── Concession ─────────────────────────────────────────────
class ConcessionRequest(BaseModel):
    from_station: str
    to_station: str
    travel_class: str  # "2S" | "SL"
    category: str      # "General" | "SC/ST" | "PH"


class ConcessionResult(BaseModel):
    from_station: str
    to_station: str
    travel_class: str
    category: str
    original_fare: int
    concession_fare: int
    savings: int
    savings_pct: int
    verified_via: str
    steps: list[str]


class StationsResponse(BaseModel):
    stations: list[str]


# ── CampusPay ──────────────────────────────────────────────
class MessBalance(BaseModel):
    balance: int
    total: int
    percentage: int


class SpendingItem(BaseModel):
    item: str
    amount: str


class Debt(BaseModel):
    name: str
    amount: int
    direction: str  # "owes_you" | "you_owe"


class SimplifiedTransaction(BaseModel):
    from_person: str
    to_person: str
    amount: int


class DebtResponse(BaseModel):
    debts: list[Debt]
    original_count: int
    simplified_count: int
    simplified_transactions: list[SimplifiedTransaction]
    message: str


class SpendingCategory(BaseModel):
    name: str
    value: int
    color: str


# ── FestPass ───────────────────────────────────────────────
class FeaturedFest(BaseModel):
    name: str
    college: str
    city: str
    dates: str
    trending: str


class Fest(BaseModel):
    name: str
    college: str
    city: str
    dates: str
    entry: int
    travel: int
    stay: int
    gradient: str


class FestListResponse(BaseModel):
    featured: FeaturedFest
    fests: list[Fest]


# ── Kharcha Report ─────────────────────────────────────────
class MonthlyTrend(BaseModel):
    month: str
    amount: int


class KharchaReport(BaseModel):
    this_month: int
    last_month: int
    savings: int
    monthly_data: list[MonthlyTrend]
    categories: list[SpendingCategory]
