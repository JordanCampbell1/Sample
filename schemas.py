from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class BlogCreate(BaseModel):
    title: str
    content: str

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class BlogOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    class from_attributes:
        orm_mode = True

class RefreshRequest(BaseModel):
    refresh_token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str