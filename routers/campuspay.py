"""CampusPay API — mess balance, spending, micro-debt tracker."""
from fastapi import APIRouter

from models import MessBalance, SpendingItem, Debt, DebtResponse, SpendingCategory
from services.debt_simplifier import simplify_debts

router = APIRouter(prefix="/api/campuspay", tags=["CampusPay"])

# ── Mock data (would come from DB in production) ──────────
_DEBTS = [
    {"name": "Rahul", "amount": 120, "direction": "owes_you"},
    {"name": "Priya", "amount": 30, "direction": "you_owe"},
    {"name": "Amit", "amount": 85, "direction": "owes_you"},
    {"name": "Neha", "amount": 45, "direction": "you_owe"},
]


@router.get("/balance", response_model=MessBalance)
async def get_balance():
    """Return current mess balance."""
    balance = 3200
    total = 5000
    return MessBalance(
        balance=balance,
        total=total,
        percentage=int((balance / total) * 100),
    )


@router.get("/spending", response_model=list[SpendingItem])
async def get_today_spending():
    """Return today's spending items."""
    return [
        SpendingItem(item="Chai", amount="₹15"),
        SpendingItem(item="Lunch", amount="₹65"),
        SpendingItem(item="Photocopy", amount="₹30"),
        SpendingItem(item="Samosa", amount="₹20"),
    ]


@router.get("/debts", response_model=DebtResponse)
async def get_debts():
    """Return debts with debt simplification applied."""
    result = simplify_debts(_DEBTS)
    return DebtResponse(
        debts=[Debt(**d) for d in result["debts"]],
        original_count=result["original_count"],
        simplified_count=result["simplified_count"],
        simplified_transactions=result["simplified_transactions"],
        message=result["message"],
    )


@router.post("/settle")
async def settle_debt(name: str):
    """Settle a debt with a friend (mock endpoint)."""
    return {
        "message": f"₹ settled with {name} via UPI! ✅",
        "upi_link": f"upi://pay?pa={name.lower()}@paytm&pn={name}&cu=INR",
    }


@router.get("/categories", response_model=list[SpendingCategory])
async def get_spending_categories():
    """Return spending breakdown by category."""
    return [
        SpendingCategory(name="Food", value=3200, color="hsl(194, 100%, 47%)"),
        SpendingCategory(name="Travel", value=1800, color="hsl(186, 100%, 50%)"),
        SpendingCategory(name="Stationery", value=600, color="hsl(43, 100%, 50%)"),
        SpendingCategory(name="Entertainment", value=1400, color="hsl(150, 80%, 44%)"),
    ]
