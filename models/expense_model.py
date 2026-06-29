from datetime import date
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    ENTERTAINMENT = "Entertainment"
    BILLS = "Bills"
    HEALTHCARE = "Healthcare"
    OTHER = "Other"


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    
    title: str
    amount: float
    category: Category
    user_id: Optional[str] = None
    date: Union[str, date, None] = None


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[Category] = None
    date: Union[str, date, None] = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "456",
                "user_id": "123",
                "title": "Lunch",
                "amount": 200,
                "category": "Food",
                "date": "2026-06-15"
            }
        }
    )
    
    id: str
    user_id: Optional[str] = None
    title: str
    amount: float
    category: Category
    date: str
