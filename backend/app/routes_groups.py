from fastapi import APIRouter, Header, HTTPException
from typing import Optional, List
from .schemas import GroupCreate
from .database import async_session
from . import crud

router = APIRouter()

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    if not authorization:
        return None
    token = authorization.split()[1]
    from .auth import decode_token
    payload = decode_token(token)
    if not payload:
        return None
    return int(payload.get('sub'))

@router.post('/')
async def create_group(data: GroupCreate, authorization: Optional[str] = Header(None)):
    user_id = await get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        g = await crud.create_group(name=data.name, owner_id=user_id, session=session)
        return {"id": g.id, "name": g.name}

@router.post('/create')
async def create_group_legacy(data: GroupCreate, authorization: Optional[str] = Header(None)):
    return await create_group(data, authorization)

@router.get('/')
async def list_groups(authorization: Optional[str] = Header(None)):
    user_id = await get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        gs = await crud.list_groups(owner_id=user_id, session=session)
        return [{"id": g.id, "name": g.name} for g in gs]

@router.get('/list')
async def list_groups_legacy(authorization: Optional[str] = Header(None)):
    return await list_groups(authorization)

@router.get('/{group_id}/members')
async def get_group_members(group_id: int, authorization: Optional[str] = Header(None)):
    user_id = await get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        members = await crud.get_group_members(group_id=group_id, session=session)
        return members
