from fastapi import APIRouter, Depends

from services.dependencies import get_current_user
from services.expense_service import (
    get_dashboard_stats,
    get_expenses_by_category,
    get_expenses_total,
    get_monthly_summary,
    get_top_category,
)

report_router = APIRouter(prefix="/summary", tags=["reports"])


@report_router.get("/")
def summary_total(user=Depends(get_current_user)):
    user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    total = get_expenses_total(user_id=user_id)
    return {"total": total}


@report_router.get("/category")
def summary_by_category(user=Depends(get_current_user)):
    user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    return get_expenses_by_category(user_id=user_id)


@report_router.get("/monthly")
def summary_monthly(user=Depends(get_current_user)):
    user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    return get_monthly_summary(user_id=user_id)


@report_router.get("/top-category")
def summary_top_category(user=Depends(get_current_user)):
    user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    top_category = get_top_category(user_id=user_id)
    return top_category or {"category": None, "amount": 0.0}


@report_router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    return get_dashboard_stats(user_id=user_id)
