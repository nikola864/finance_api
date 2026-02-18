from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v.lower() in ['admin', 'administrator', 'root']:
            raise ValueError("Это имя пользователя зарезервировано")
        return v

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_math(cls, v, info):
        if "new_password" in info.data and v != info.data['new_password']:
            raise ValueError("Пароли не совпадают")
        return v

class UserResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    user: UserRead
























