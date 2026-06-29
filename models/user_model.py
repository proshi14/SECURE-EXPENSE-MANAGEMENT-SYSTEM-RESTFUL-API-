from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "123",
                "username": "roshini",
                "email": "roshini@gmail.com"
            }
        }
    )
    
    id: str = Field(..., alias="_id")
    username: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
