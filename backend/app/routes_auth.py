from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from .schemas import UserCreate, Token, UserOut
from .database import async_session
from . import crud
from .auth import create_access_token
from contextlib import asynccontextmanager

router = APIRouter()

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        yield session

@router.post('/register', response_model=UserOut)
async def register(user: UserCreate):
    async with async_session() as session:
        existing = await crud.get_user_by_email(user.email, session)
        if existing:
            raise HTTPException(status_code=400, detail='Email already registered')
        new_user = await crud.create_user(user.email, user.password, user.full_name, user.is_teacher, session)
        return new_user

@router.post('/login', response_model=Token)
async def login(form: UserCreate):
    async with async_session() as session:
        user = await crud.verify_user(form.email, form.password, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        token = create_access_token({
            "sub": str(user.id), 
            "email": user.email,
            "is_teacher": user.is_teacher,
            "permissions": ["read", "write", "ai_query"]
        })
        return {"access_token": token, "token_type": "bearer"}

@router.get('/users/search')
async def search_users(q: str, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        users = await crud.search_users(query=q, session=session)
        return users
