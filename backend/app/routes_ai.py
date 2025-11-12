from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from .schemas import AIQuery
from .database import async_session
from . import crud
import os

router = APIRouter()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')


@router.post('/query')
async def ai_query(query_payload: AIQuery, authorization: Optional[str] = Header(None)):
    """AI-powered email search and summarization"""
    
    # Authenticate user
    if not authorization:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    try:
        token = authorization.split()[1]
        from .auth import decode_token
        token_payload = decode_token(token)
        if not token_payload or "ai_query" not in token_payload.get("permissions", []):
            raise HTTPException(status_code=403, detail='Permission denied')
        user = token_payload.get('email')
        if not user:
            raise HTTPException(status_code=401, detail='Invalid token')
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Authentication failed: {str(e)}')

    async with async_session() as session:
        # Retrieve relevant messages
        try:
            msgs = await crud.retrieve_similar_messages(
                query_payload.query,
                group_id=getattr(query_payload, 'group_id', 0),
                since_days=getattr(query_payload, 'since_days', 7),
                top_k=20,
                session=session,
                owner_email=user,
            )
        except Exception:
            msgs = await crud.retrieve_messages_for_group(
                group_id=getattr(query_payload, 'group_id', 0),
                since_days=getattr(query_payload, 'since_days', 7),
                session=session,
                owner_email=user,
            )

        if not msgs:
            return {"answer": "No relevant emails found for your query."}

        # Build context from retrieved messages
        context_parts = []
        for m in msgs[:10]:
            context_parts.append(
                f"[msg:{m.id}] From: {m.sender} | Subject: {m.subject or 'No subject'}\n{m.body[:500]}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Prepare messages for LLM
        system_msg = (
            "You are an AI assistant helping with email search. "
            "Analyze the provided emails and synthesize a comprehensive answer. "
            "Always cite sources using [msg:ID] format."
        )
        user_msg = f"Question: {query_payload.query}\n\nRelevant emails:\n{context}\n\nAnswer:"

        answer = None

        # Try OpenAI if available
        if OPENAI_KEY:
            try:
                import openai
                from openai import OpenAI as OpenAIClient
                
                client = OpenAIClient(api_key=OPENAI_KEY)
                resp = client.chat.completions.create(
                    model=OPENAI_CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    max_tokens=300,
                    temperature=0.2,
                )
                answer = resp.choices[0].message.content.strip()
            except Exception as e:
                print(f"[AI] OpenAI error: {e}")

        # Smart local fallback
        if not answer:
            q_lower = query_payload.query.lower()
            is_summary = any(w in q_lower for w in ['summarize', 'summary', 'what'])
            is_latest = any(w in q_lower for w in ['latest', 'recent', 'newest', 'last'])
            
            top_msgs = msgs[:5]
            
            if is_latest and top_msgs:
                latest = top_msgs[0]
                answer = (
                    f"**Latest Email** [msg:{latest.id}]\n\n"
                    f"**From:** {latest.sender}\n"
                    f"**Subject:** {latest.subject or 'No subject'}\n"
                    f"**Date:** {latest.timestamp.strftime('%Y-%m-%d %H:%M') if latest.timestamp else 'Unknown'}\n\n"
                    f"**Content:**\n{latest.body[:500]}{'...' if len(latest.body or '') > 500 else ''}\n\n"
                    f"_Found {len(msgs)} matching messages._"
                )
            elif is_summary and top_msgs:
                parts = [f"**Summary of {len(top_msgs)} Relevant Emails:**\n"]
                for i, msg in enumerate(top_msgs[:3], 1):
                    preview = (msg.body or '')[:200].replace('\n', ' ')
                    parts.append(
                        f"\n{i}. **[msg:{msg.id}]** From {msg.sender}\n"
                        f"   Subject: {msg.subject or 'No subject'}\n"
                        f"   {preview}{'...' if len(msg.body or '') > 200 else ''}"
                    )
                answer = '\n'.join(parts)
            else:
                answer = f"**Found {len(msgs)} relevant emails:**\n\n" + '\n\n'.join([
                    f"**[msg:{m.id}]** {m.subject or 'No subject'}\n"
                    f"From: {m.sender}\n{(m.body or '')[:200]}..."
                    for m in top_msgs[:3]
                ])

        # Cache response
        try:
            await crud.cache_ai_response(query_payload.query, answer, session)
        except Exception:
            pass

        return {"answer": answer}
