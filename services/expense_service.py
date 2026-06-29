from bson import ObjectId
from datetime import date
from typing import Optional

from pymongo import ASCENDING, DESCENDING, ReturnDocument

from database.connection import expenses_collection
from models.expense_model import Category, ExpenseCreate, ExpenseUpdate


def normalize_expense(expense: dict) -> dict:
    if not expense:
        return None
    expense["id"] = str(expense.pop("_id"))
    if isinstance(expense.get("date"), date):
        expense["date"] = expense["date"].isoformat()
    return expense


def build_expense_query(
    user_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
    category: Optional[Category] = None,
) -> dict:
    query = {}
    if user_id is not None:
        query["user_id"] = user_id

    if category is not None:
        query["category"] = category.value if isinstance(category, Category) else category

    if start_date is not None or end_date is not None:
        date_filter = {}
        if start_date is not None:
            date_filter["$gte"] = start_date.isoformat()
        if end_date is not None:
            date_filter["$lte"] = end_date.isoformat()
        if date_filter:
            query["date"] = date_filter

    if keyword is not None:
        query["title"] = {"$regex": keyword, "$options": "i"}

    return query


def create_expense(expense: ExpenseCreate, user_id: Optional[str] = None):
    expense_dict = expense.dict(exclude_none=True)
    if isinstance(expense_dict.get("category"), Category):
        expense_dict["category"] = expense_dict["category"].value

    expense_dict["_id"] = str(ObjectId())
    
    # Handle date field - convert string to date if needed
    date_value = expense_dict.get("date")
    if date_value is None:
        expense_dict["date"] = date.today().isoformat()
    elif isinstance(date_value, str):
        # Parse string date to ensure it's valid, then store as ISO string
        try:
            parsed_date = date.fromisoformat(date_value)
            expense_dict["date"] = parsed_date.isoformat()
        except (ValueError, TypeError):
            expense_dict["date"] = date.today().isoformat()
    elif isinstance(date_value, date):
        expense_dict["date"] = date_value.isoformat()
    else:
        expense_dict["date"] = date.today().isoformat()
    
    if user_id is not None:
        expense_dict["user_id"] = user_id

    expenses_collection.insert_one(expense_dict)
    return normalize_expense(expense_dict)


def get_all_expenses(
    user_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    limit: Optional[int] = 10,
    category: Optional[Category] = None,
):
    query = build_expense_query(user_id=user_id, start_date=start_date, end_date=end_date, keyword=keyword, category=category)
    cursor = expenses_collection.find(query)

    if sort_by in {"amount", "date", "category", "title"}:
        cursor = cursor.sort(sort_by, ASCENDING)

    if page < 1:
        page = 1
    if limit is None:
        pass
    else:
        if limit < 1:
            limit = 10
        cursor = cursor.skip((page - 1) * limit).limit(limit)

    return [normalize_expense(expense) for expense in cursor]


def get_expense_by_id(expense_id: str):
    return normalize_expense(expenses_collection.find_one({"_id": expense_id}))


def update_expense(expense_id: str, expense: ExpenseUpdate):
    updated_data = expense.dict(exclude_none=True)
    if "category" in updated_data and isinstance(updated_data["category"], Category):
        updated_data["category"] = updated_data["category"].value
    if "date" in updated_data:
        date_value = updated_data["date"]
        if isinstance(date_value, str):
            try:
                parsed_date = date.fromisoformat(date_value)
                updated_data["date"] = parsed_date.isoformat()
            except (ValueError, TypeError):
                pass
        elif isinstance(date_value, date):
            updated_data["date"] = date_value.isoformat()

    result = expenses_collection.find_one_and_update(
        {"_id": expense_id},
        {"$set": updated_data},
        return_document=ReturnDocument.AFTER,
    )
    return normalize_expense(result)


def delete_expense(expense_id: str) -> bool:
    result = expenses_collection.delete_one({"_id": expense_id})
    return result.deleted_count == 1


def get_expenses_total(user_id: Optional[str] = None) -> float:
    pipeline = []
    if user_id is not None:
        pipeline.append({"$match": {"user_id": user_id}})
    pipeline.append({"$group": {"_id": None, "total": {"$sum": "$amount"}}})

    result = list(expenses_collection.aggregate(pipeline))
    if not result:
        return 0.0
    return float(result[0]["total"])


def get_expenses_by_category(user_id: Optional[str] = None) -> dict:
    pipeline = []
    if user_id is not None:
        pipeline.append({"$match": {"user_id": user_id}})
    pipeline.append({"$group": {"_id": "$category", "total": {"$sum": "$amount"}}})

    result = expenses_collection.aggregate(pipeline)
    return {item["_id"]: float(item["total"]) for item in result}


def get_top_category(user_id: Optional[str] = None) -> Optional[dict]:
    pipeline = []
    if user_id is not None:
        pipeline.append({"$match": {"user_id": user_id}})
    pipeline.extend([
        {"$group": {"_id": "$category", "amount": {"$sum": "$amount"}}},
        {"$sort": {"amount": -1}},
        {"$limit": 1},
    ])

    result = list(expenses_collection.aggregate(pipeline))
    if not result:
        return None
    return {"category": result[0]["_id"], "amount": float(result[0]["amount"])}


def get_monthly_summary(user_id: Optional[str] = None) -> dict:
    pipeline = []
    if user_id is not None:
        pipeline.append({"$match": {"user_id": user_id}})
    pipeline.extend([
        {
            "$addFields": {
                "year": {"$substr": ["$date", 0, 4]},
                "month": {"$substr": ["$date", 5, 2]},
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "month": "$month"},
                "total": {"$sum": "$amount"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ])

    result = list(expenses_collection.aggregate(pipeline))
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    summary = {}
    for item in result:
        year = item["_id"]["year"]
        month_index = int(item["_id"]["month"])
        month_name = month_names[month_index - 1]
        summary[f"{month_name}-{year}"] = float(item["total"])
    return summary


def get_dashboard_stats(user_id: Optional[str] = None) -> dict:
    query = {"user_id": user_id} if user_id is not None else {}
    total = get_expenses_total(user_id=user_id)
    total_transactions = expenses_collection.count_documents(query)
    highest_expense_doc = expenses_collection.find(query).sort("amount", DESCENDING).limit(1)
    highest_expense = 0.0
    for doc in highest_expense_doc:
        highest_expense = float(doc.get("amount", 0.0))
        break

    top_category = get_top_category(user_id=user_id)
    return {
        "total_expenses": total,
        "total_transactions": total_transactions,
        "highest_expense": highest_expense,
        "top_category": top_category["category"] if top_category else None,
    }
