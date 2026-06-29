from fastapi import APIRouter, HTTPException

from models.user_model import TokenResponse, UserCreate, UserLogin, UserResponse
from services.auth_service import create_user, login_user

user_router = APIRouter()


@user_router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    created = create_user(user)
    if not created:
        raise HTTPException(status_code=400, detail="Email is already registered")
    return created


@user_router.post("/login", response_model=TokenResponse)
def login_user_route(credentials: UserLogin):
    token = login_user(credentials.email, credentials.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return token
