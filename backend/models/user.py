from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str
    username: str
    email: str
    phone: str
    password_hash: str
    role: str  # lab, doctor, staff, admin
    status: str = "active"  # active, inactive
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    id: str
    username: str
    email: str
    phone: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str
    role: str