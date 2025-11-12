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

@router.delete('/delete/{msg_id}')
async def delete_mail(msg_id: int, authorization: Optional[str] = Header(None)):
    email = await get_current_user_email(authorization)
    if not email:
        raise HTTPException(status_code=401, detail='Unauthorized')
    async with async_session() as session:
        ok = await crud.delete_message(msg_id=msg_id, owner_email=email, session=session)
        if not ok:
            raise HTTPException(status_code=404, detail='Message not found or not permitted')
        return {"deleted": True}
