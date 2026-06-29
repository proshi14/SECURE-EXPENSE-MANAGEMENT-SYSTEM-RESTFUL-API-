import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "expense_tracker")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
except Exception as e:
    raise RuntimeError(f"Unable to connect to MongoDB at {MONGO_URI}: {e}")

# Database and collection references
db = client[DB_NAME]

# Ensure collections exist explicitly so db.users and db.expenses work immediately.
if "users" not in db.list_collection_names():
    db.create_collection("users")

if "expenses" not in db.list_collection_names():
    db.create_collection("expenses")

users_collection = db["users"]
expenses_collection = db["expenses"]
