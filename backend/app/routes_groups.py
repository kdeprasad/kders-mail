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

@router.post('')
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

@router.get('')
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

@router.post('/{group_id}/members')
async def add_group_member(group_id: int, data: dict, authorization: Optional[str] = Header(None)):
    """Add a member to a group by email"""
    user_id = await get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    email = data.get('email')
    if not email:
        raise HTTPException(status_code=400, detail='Email required')
    
    async with async_session() as session:
        # Check if user is group owner
        from .models import Group
        from sqlalchemy import select
        result = await session.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()
        if not group or group.owner_id != user_id:
            raise HTTPException(status_code=403, detail='Only group owner can add members')
        
        # Get user by email
        target_user = await crud.get_user_by_email(email, session)
        if not target_user:
            raise HTTPException(status_code=404, detail='User not found')
        
        # Add member
        await crud.add_member(group_id=group_id, user_id=target_user.id, session=session)
        return {"message": "Member added successfully", "user": {"email": target_user.email, "full_name": target_user.full_name}}

@router.delete('/{group_id}/members/{user_id}')
async def remove_group_member(group_id: int, user_id: int, authorization: Optional[str] = Header(None)):
    """Remove a member from a group"""
    current_user_id = await get_current_user_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    async with async_session() as session:
        # Check if user is group owner
        from .models import Group, GroupMember
        from sqlalchemy import select, delete
        result = await session.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()
        if not group or group.owner_id != current_user_id:
            raise HTTPException(status_code=403, detail='Only group owner can remove members')
        
        # Remove member
        await session.execute(delete(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ))
        await session.commit()
        return {"message": "Member removed successfully"}

@router.post('/{group_id}/send')
async def send_group_message(group_id: int, data: dict, authorization: Optional[str] = Header(None)):
    """Send a message to all members of a group"""
    user_id = await get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    subject = data.get('subject', '')
    body = data.get('body', '')
    
    async with async_session() as session:
        # Get sender email
        from .models import User
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.id == user_id))
        sender_user = result.scalar_one_or_none()
        if not sender_user:
            raise HTTPException(status_code=404, detail='Sender not found')
        
        sender_email = sender_user.email
        
        # Get all group members
        members = await crud.get_group_members(group_id=group_id, session=session)
        
        # Send message to each member
        sent_count = 0
        for member in members:
            if member['email'] != sender_email:  # Don't send to self
                await crud.create_message(
                    sender=sender_email,
                    recipient=member['email'],
                    subject=f"[Group] {subject}",
                    body=body,
                    owner_id=None,
                    session=session
                )
                sent_count += 1
        
        return {"message": f"Message sent to {sent_count} members", "recipients": sent_count}
