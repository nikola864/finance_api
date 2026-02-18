from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class AuthResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    token: Token
    user: dict