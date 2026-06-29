import bcrypt
import os
from bson import ObjectId

from database.connection import users_collection
from models.user_model import UserCreate
from services.jwt_service import create_access_token


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_user(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        return None

    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user_dict["password"])
    user_dict["_id"] = str(ObjectId())

    users_collection.insert_one(user_dict)
    return {"_id": user_dict["_id"], "username": user_dict["username"], "email": user_dict["email"]}


def authenticate_user(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None

    return {"_id": str(user["_id"]), "username": user["username"], "email": user["email"]}


def login_user(email: str, password: str):
    user = authenticate_user(email, password)
    if not user:
        return None

    access_token = create_access_token({"sub": user["_id"], "email": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


def get_user_by_id(user_id: str):
    return users_collection.find_one({"_id": user_id})
