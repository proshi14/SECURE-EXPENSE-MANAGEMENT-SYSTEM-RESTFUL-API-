from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.dependencies import get_current_user
from services.expense_service import get_all_expenses

export_router = APIRouter(prefix="/export", tags=["export"])


def _get_user_id(user: Any) -> str | None:
    if isinstance(user, dict):
        return user.get("sub") or user.get("_id") or user.get("user_id")
    return None


@export_router.get("/excel")
def export_excel(user=Depends(get_current_user)):
    user_id = _get_user_id(user)
    expenses = get_all_expenses(user_id=user_id, page=1, limit=100000)

    df = pd.DataFrame(expenses)
    if df.empty:
        df = pd.DataFrame(columns=["id", "title", "amount", "category", "date"])
    else:
        # Reorder columns to match the normalized field names
        df = df[["id", "title", "amount", "category", "date"]]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Expenses")

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=expenses.xlsx"},
    )


@export_router.get("/pdf")
def export_pdf(user=Depends(get_current_user)):
    user_id = _get_user_id(user)
    expenses = get_all_expenses(user_id=user_id, page=1, limit=100000)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Expense Report", styles["Title"]), Spacer(1, 12)]

    if not expenses:
        elements.append(Paragraph("No expenses found for this user.", styles["Normal"]))
    else:
        data = [["Title", "Amount", "Category", "Date"]]
        for expense in expenses:
            data.append([
                expense.get("title", ""),
                f"{expense.get('amount', 0.0):.2f}",
                expense.get("category", ""),
                expense.get("date", ""),
            ])

        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "LEFT"),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=expenses.pdf"},
    )
