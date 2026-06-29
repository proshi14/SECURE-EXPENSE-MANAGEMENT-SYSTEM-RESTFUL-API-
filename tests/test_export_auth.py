import os
from pathlib import Path

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "expense_export.xlsx"
PDF_FILE = BASE_DIR / "expense_export.pdf"


def ensure_data():
    user = {"username": "exportuser", "email": "exportuser@example.com", "password": "password123"}
    resp = client.post("/users/register", json=user)
    if resp.status_code not in (200, 400):
        raise RuntimeError(f"Register failed: {resp.status_code} {resp.text}")

    resp = client.post("/users/login", json={"email": user["email"], "password": user["password"]})
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    token = resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    expense = {"title": "Test Expense", "amount": 10.0, "category": "Food"}
    resp = client.post("/expenses/", json=expense, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Create expense failed: {resp.status_code} {resp.text}")
    return headers


def test_export_endpoints():
    headers = ensure_data()

    resp = client.get("/export/excel", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    with open(EXCEL_FILE, "wb") as f:
        f.write(resp.content)

    resp = client.get("/export/pdf", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    with open(PDF_FILE, "wb") as f:
        f.write(resp.content)

    print(f"Saved {EXCEL_FILE} and {PDF_FILE}")


if __name__ == "__main__":
    test_export_endpoints()
