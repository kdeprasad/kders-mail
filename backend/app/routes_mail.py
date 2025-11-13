from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from . import schemas
from .database import async_session
from typing import List, Optional

router = APIRouter()

async def get_current_user_email(authorization: Optional[str] = Header(None)) -> Optional[str]:
    # simplistic: expects Bearer <token> and token contains email in payload
    if not authorization:
        return None
    try:
        token = authorization.split()[1]
    except Exception:
        return None
    from .auth import decode_token
    payload = decode_token(token)
    if not payload:
        return None
    return payload.get('email')

@router.post('/compose', response_model=schemas.MessageOut)
async def compose_mail(msg: schemas.MessageCreate, authorization: Optional[str] = Header(None)):
    sender = await get_current_user_email(authorization)
    if not sender:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        # create message and store
        created = await crud.create_message(sender=sender, recipient=msg.recipient, subject=msg.subject, body=msg.body, owner_id=None, session=session)
        return created

@router.get('/inbox', response_model=List[schemas.MessageOut])
async def inbox(limit: int = 50, authorization: Optional[str] = Header(None)):
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        msgs = await crud.list_inbox(email=email, limit=limit, session=session)
        return msgs

@router.delete('/{msg_id}')
async def delete_mail(msg_id: int, authorization: Optional[str] = Header(None)):
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        ok = await crud.delete_message(msg_id=msg_id, owner_email=email, session=session)
        if not ok:
            raise HTTPException(status_code=404, detail='Message not found or not permitted')
        return {"deleted": True}

@router.patch('/{msg_id}/read')
async def mark_as_read(msg_id: int, data: dict, authorization: Optional[str] = Header(None)):
    """Mark message as read/unread"""
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    is_read = data.get('is_read', True)
    
    async with async_session() as session:
        from .models import Message
        from sqlalchemy import select, update
        
        # Verify user owns this message (recipient)
        result = await session.execute(select(Message).where(Message.id == msg_id))
        msg = result.scalar_one_or_none()
        if not msg or msg.recipient != email:
            raise HTTPException(status_code=404, detail='Message not found')
        
        # Update read status
        await session.execute(
            update(Message).where(Message.id == msg_id).values(is_read=is_read)
        )
        await session.commit()
        return {"message": "Read status updated", "is_read": is_read}

@router.patch('/{msg_id}/pin')
async def toggle_pin(msg_id: int, data: dict, authorization: Optional[str] = Header(None)):
    """Pin/unpin a message"""
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    is_pinned = data.get('is_pinned', True)
    
    async with async_session() as session:
        from .models import Message
        from sqlalchemy import select, update
        
        # Verify user owns this message (recipient)
        result = await session.execute(select(Message).where(Message.id == msg_id))
        msg = result.scalar_one_or_none()
        if not msg or msg.recipient != email:
            raise HTTPException(status_code=404, detail='Message not found')
        
        # Update pinned status
        await session.execute(
            update(Message).where(Message.id == msg_id).values(is_pinned=is_pinned)
        )
        await session.commit()
        return {"message": "Pin status updated", "is_pinned": is_pinned}

@router.get('/search')
async def search_mail(q: str, authorization: Optional[str] = Header(None)):
    """Search emails by subject, sender, or body"""
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    if not q or len(q) < 2:
        return []
    
    async with async_session() as session:
        from .models import Message
        from sqlalchemy import select, or_
        
        query = select(Message).where(
            Message.recipient == email,
            or_(
                Message.subject.ilike(f'%{q}%'),
                Message.sender.ilike(f'%{q}%'),
                Message.body.ilike(f'%{q}%')
            )
        ).order_by(Message.timestamp.desc()).limit(50)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        return messages
