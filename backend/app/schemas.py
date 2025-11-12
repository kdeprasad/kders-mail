from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]
    is_teacher: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_teacher: bool
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    subject: Optional[str]
    body: str
    recipient: str

class MessageOut(BaseModel):
    id: int
    subject: Optional[str]
    body: str
    sender: str
    recipient: str
    timestamp: datetime
    class Config:
        orm_mode = True

class GroupCreate(BaseModel):
    name: str

class AIQuery(BaseModel):
    query: str
    group_id: Optional[int] = None
    since_days: Optional[int] = 7
