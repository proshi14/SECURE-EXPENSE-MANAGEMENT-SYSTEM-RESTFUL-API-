from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from models.expense_model import Category, ExpenseCreate, ExpenseResponse, ExpenseUpdate
from services.dependencies import get_current_user
from services.expense_service import (
    create_expense,
    delete_expense,
    get_all_expenses,
    get_expense_by_id,
    update_expense,
)
from services.jwt_service import decode_access_token

expense_router = APIRouter(prefix="/expenses", tags=["expenses"])


@expense_router.post("/", response_model=ExpenseResponse)
def add_expense(expense: ExpenseCreate, user=Depends(get_current_user), request: Request = None):
    user_id = None
    if isinstance(user, dict):
        user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    # fallback: try to read Authorization header
    if not user_id and request is not None:
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            payload = decode_access_token(auth.split(" ", 1)[1])
            if payload:
                user_id = payload.get("sub") or payload.get("_id") or payload.get("user_id")
    created = create_expense(expense, user_id=user_id)
    if not created:
        raise HTTPException(status_code=400, detail="Expense creation failed")
    return created


@expense_router.get("/", response_model=list[ExpenseResponse])
def list_expenses(
    user=Depends(get_current_user),
    request: Request = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    category: Optional[Category] = Query(None),
    sort: Optional[str] = Query(None, pattern="^(amount|date|category|title)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    user_id = None
    if isinstance(user, dict):
        user_id = user.get("sub") or user.get("_id") or user.get("user_id")
    if not user_id and request is not None:
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            payload = decode_access_token(auth.split(" ", 1)[1])
            if payload:
                user_id = payload.get("sub") or payload.get("_id") or payload.get("user_id")
    return get_all_expenses(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        keyword=keyword,
        sort_by=sort,
        page=page,
        limit=limit,
        category=category,
    )


@expense_router.get("/{expense_id}", response_model=ExpenseResponse)
def read_expense(expense_id: str, user=Depends(get_current_user)):
    expense = get_expense_by_id(expense_id)
    if not expense or expense.get("user_id") != (user.get("sub") or user.get("_id")):
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@expense_router.put("/{expense_id}", response_model=ExpenseResponse)
def edit_expense(expense_id: str, expense: ExpenseUpdate, user=Depends(get_current_user)):
    existing = get_expense_by_id(expense_id)
    if not existing or existing.get("user_id") != (user.get("sub") or user.get("_id")):
        raise HTTPException(status_code=404, detail="Expense not found or not owned by user")
    updated = update_expense(expense_id, expense)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found or no fields provided")
    return updated


@expense_router.delete("/{expense_id}")
def remove_expense(expense_id: str, user=Depends(get_current_user)):
    existing = get_expense_by_id(expense_id)
    if not existing or existing.get("user_id") != (user.get("sub") or user.get("_id")):
        raise HTTPException(status_code=404, detail="Expense not found or not owned by user")
    deleted = delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
