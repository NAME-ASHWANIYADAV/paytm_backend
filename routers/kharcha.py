"""Kharcha Report API — monthly spending analytics."""
from fastapi import APIRouter

from models import KharchaReport, MonthlyTrend, SpendingCategory

router = APIRouter(prefix="/api/kharcha", tags=["Kharcha Report"])


@router.get("/report", response_model=KharchaReport)
async def get_report():
    """Return monthly spending report with trends and category breakdown."""
    this_month = 3400
    last_month = 4600
    savings = last_month - this_month

    monthly_data = [
        MonthlyTrend(month="Sep", amount=4200),
        MonthlyTrend(month="Oct", amount=5100),
        MonthlyTrend(month="Nov", amount=3800),
        MonthlyTrend(month="Dec", amount=6200),
        MonthlyTrend(month="Jan", amount=4600),
        MonthlyTrend(month="Feb", amount=3400),
    ]

    categories = [
        SpendingCategory(name="Food", value=3200, color="hsl(194, 100%, 47%)"),
        SpendingCategory(name="Travel", value=1800, color="hsl(186, 100%, 50%)"),
        SpendingCategory(name="Stationery", value=600, color="hsl(43, 100%, 50%)"),
        SpendingCategory(name="Entertainment", value=1400, color="hsl(150, 80%, 44%)"),
        SpendingCategory(name="Recharge", value=500, color="hsl(0, 84%, 60%)"),
    ]

    return KharchaReport(
        this_month=this_month,
        last_month=last_month,
        savings=savings,
        monthly_data=monthly_data,
        categories=categories,
    )
