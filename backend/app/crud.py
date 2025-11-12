from sqlalchemy.future import select
from sqlalchemy import insert
from passlib.context import CryptContext
from .models import User, Message, Group, GroupMember, AICache
from .database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import os
from sqlalchemy import text
import math
import httpx

# external embedding providers
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_KEY = os.getenv('HUGGINGFACE_API_KEY')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
HUGGINGFACE_EMBEDDING_MODEL = os.getenv('HUGGINGFACE_EMBEDDING_MODEL', os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'))

# embedding configuration
PGVECTOR_ENABLED = os.getenv('PGVECTOR_ENABLED', 'false').lower() in ('1', 'true', 'yes')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
embedding_model = None
if PGVECTOR_ENABLED:
    try:
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    except Exception:
        embedding_model = None

# Simple in-memory LRU cache for embeddings (hosted embeddings path)
EMBEDDING_CACHE_SIZE = int(os.getenv('EMBEDDING_CACHE_SIZE', '1024'))
_embedding_cache = {}
_embedding_cache_order = []

def _cache_get(key: str):
    return _embedding_cache.get(key)

def _cache_set(key: str, vec):
    # simple LRU: keep insertion order, pop oldest when over capacity
    if key in _embedding_cache:
        try:
            _embedding_cache_order.remove(key)
        except ValueError:
            pass
    _embedding_cache[key] = vec
    _embedding_cache_order.append(key)
    if len(_embedding_cache_order) > EMBEDDING_CACHE_SIZE:
        old = _embedding_cache_order.pop(0)
        _embedding_cache.pop(old, None)

# Use pbkdf2_sha256 to avoid native bcrypt wheel issues in some environments
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

async def get_user_by_email(email: str, session: AsyncSession) -> Optional[User]:
    q = await session.execute(select(User).where(User.email == email))
    return q.scalars().first()

async def create_user(email: str, password: str, full_name: Optional[str], is_teacher: bool, session: AsyncSession) -> User:
    hashed = pwd_ctx.hash(password)
    user = User(email=email, hashed_password=hashed, full_name=full_name, is_teacher=is_teacher)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def verify_user(email: str, password: str, session: AsyncSession) -> Optional[User]:
    user = await get_user_by_email(email, session)
    if not user:
        return None
    if not pwd_ctx.verify(password, user.hashed_password):
        return None
    return user

async def create_message(sender: str, recipient: str, subject: Optional[str], body: str, owner_id: Optional[int], session: AsyncSession) -> Message:
    # Insert explicitly without referencing the model's `embedding` column to avoid
    # SQL being generated that touches a DB column which may not exist.
    ts = datetime.utcnow()
    # compute embedding if local embedding_model present and DB has column (we won't include it in the INSERT)
    emb_list = None
    if embedding_model is not None:
        try:
            vec = embedding_model.encode(body or '')
            emb_list = vec.tolist() if hasattr(vec, 'tolist') else list(vec)
        except Exception:
            emb_list = None

    # Use explicit INSERT that does not include the embedding column. If/when the
    # embedding column exists and you want to persist it, run an ALTER TABLE and
    # use an UPDATE to write the vector later (or enable pgvector path).
    stmt = insert(Message).values(
        subject=subject,
        body=body,
        sender=sender,
        recipient=recipient,
        timestamp=ts,
        owner_id=owner_id,
        mail_raw=None,
    ).returning(
        Message.id,
        Message.subject,
        Message.body,
        Message.sender,
        Message.recipient,
        Message.timestamp,
        Message.owner_id,
        Message.mail_raw,
    )
    res = await session.execute(stmt)
    await session.commit()
    row = res.fetchone()
    # Construct a Message-like object to return (not attached to session)
    msg = Message(
        id=row._mapping['id'],
        subject=row._mapping['subject'],
        body=row._mapping['body'],
        sender=row._mapping['sender'],
        recipient=row._mapping['recipient'],
        timestamp=row._mapping['timestamp'],
        owner_id=row._mapping['owner_id'],
        mail_raw=row._mapping['mail_raw'],
    )
    # If we computed an embedding and the DB actually has an embedding column,
    # persist it via an UPDATE so we only touch that column when it's present.
    if emb_list is not None:
        try:
            col_check = await session.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='embedding' LIMIT 1"))
            has_col = col_check.scalar() is not None
        except Exception:
            has_col = False
        if has_col:
            try:
                await session.execute(text("UPDATE messages SET embedding = :vec WHERE id = :id"), {'vec': emb_list, 'id': msg.id})
                await session.commit()
            except Exception:
                # don't fail the whole flow if updating embedding isn't possible
                pass
    return msg

async def list_inbox(email: str, limit: int, session: AsyncSession) -> List[Message]:
    q = await session.execute(select(Message).where(Message.recipient == email).order_by(Message.timestamp.desc()).limit(limit))
    return q.scalars().all()

async def delete_message(msg_id: int, owner_email: str, session: AsyncSession) -> bool:
    q = await session.execute(select(Message).where(Message.id == msg_id))
    msg = q.scalars().first()
    if not msg or msg.recipient != owner_email:
        return False
    await session.delete(msg)
    await session.commit()
    return True
    return True

async def create_group(name: str, owner_id: int, session: AsyncSession) -> Group:
    g = Group(name=name, owner_id=owner_id)
    session.add(g)
    await session.commit()
    await session.refresh(g)
    return g

async def list_groups(owner_id: int, session: AsyncSession):
    q = await session.execute(select(Group).where(Group.owner_id == owner_id))
    return q.scalars().all()

async def add_member(group_id: int, user_id: int, session: AsyncSession):
    gm = GroupMember(group_id=group_id, user_id=user_id)
    session.add(gm)
    await session.commit()
    await session.refresh(gm)
    return gm

async def get_group_members(group_id: int, session: AsyncSession):
    """Get all members of a group with their email addresses"""
    q = await session.execute(
        select(User.id, User.email, User.full_name)
        .join(GroupMember, GroupMember.user_id == User.id)
        .where(GroupMember.group_id == group_id)
    )
    rows = q.fetchall()
    return [{"id": r[0], "email": r[1], "full_name": r[2]} for r in rows]

async def search_users(query: str, session: AsyncSession, limit: int = 20):
    """Search users by email or name"""
    pattern = f"%{query}%"
    q = await session.execute(
        select(User.id, User.email, User.full_name, User.is_teacher)
        .where((User.email.ilike(pattern)) | (User.full_name.ilike(pattern)))
        .limit(limit)
    )
    rows = q.fetchall()
    return [{"id": r[0], "email": r[1], "full_name": r[2], "is_teacher": r[3]} for r in rows]

async def cache_ai_response(query: str, response: str, session: AsyncSession):
    c = AICache(query=query, response=response)
    session.add(c)
    await session.commit()
    await session.refresh(c)
    return c

async def retrieve_messages_for_group(group_id: int, since_days: int, session: AsyncSession, owner_email: Optional[str] = None):
    # Simple retrieval: find messages where recipient matches group name or group members; placeholder for real implementation
    since = datetime.utcnow() - timedelta(days=since_days)
    # Select explicit columns to avoid referencing an embedding column that may not exist in DB
    stmt = select(
        Message.id,
        Message.subject,
        Message.body,
        Message.sender,
        Message.recipient,
        Message.timestamp,
        Message.owner_id,
        Message.mail_raw,
    )
    # filter by time and, if provided, by recipient (current user)
    if owner_email:
        stmt = stmt.where(Message.timestamp >= since, Message.recipient == owner_email)
    else:
        stmt = stmt.where(Message.timestamp >= since)
    stmt = stmt.order_by(Message.timestamp.desc()).limit(500)
    res = await session.execute(stmt)
    rows = res.fetchall()
    msgs = []
    for r in rows:
        m = Message(
            id=r._mapping['id'],
            subject=r._mapping['subject'],
            body=r._mapping['body'],
            sender=r._mapping['sender'],
            recipient=r._mapping['recipient'],
            timestamp=r._mapping['timestamp'],
            owner_id=r._mapping['owner_id'],
            mail_raw=r._mapping['mail_raw'],
        )
        msgs.append(m)
    return msgs


async def retrieve_similar_messages(query: str, group_id: int, since_days: int, top_k: int, session: AsyncSession, owner_email: Optional[str] = None):
    """Try pgvector-backed SQL k-NN if available, otherwise use hosted-embeddings retrieval.
    Falls back to recent messages if embeddings/providers aren't available or on error.
    """
    # if pgvector path available (we rely on PGVECTOR_ENABLED and embedding_model for local vectors)
    if PGVECTOR_ENABLED and embedding_model is not None:
        try:
            vec = embedding_model.encode(query or '')
            vec_list = vec.tolist() if hasattr(vec, 'tolist') else list(vec)
            since = datetime.utcnow() - timedelta(days=since_days)
            base_sql = """
                SELECT id FROM messages
                WHERE timestamp >= :since {recipient_filter}
                ORDER BY embedding <-> :vec
                LIMIT :k
            """
            recipient_filter = "AND recipient = :recipient" if owner_email else ""
            sql = text(base_sql.format(recipient_filter=recipient_filter))
            params = {'since': since, 'vec': vec_list, 'k': top_k}
            if owner_email:
                params['recipient'] = owner_email
            res = await session.execute(sql, params)
            rows = res.fetchall()
            ids = [r[0] for r in rows]
            if ids:
                # fetch explicit columns to avoid referencing embedding column
                stmt = select(
                    Message.id,
                    Message.subject,
                    Message.body,
                    Message.sender,
                    Message.recipient,
                    Message.timestamp,
                    Message.owner_id,
                    Message.mail_raw,
                ).where(Message.id.in_(ids))
                q = await session.execute(stmt)
                rows = q.fetchall()
                msgs = []
                for r in rows:
                    m = Message(
                        id=r._mapping['id'],
                        subject=r._mapping['subject'],
                        body=r._mapping['body'],
                        sender=r._mapping['sender'],
                        recipient=r._mapping['recipient'],
                        timestamp=r._mapping['timestamp'],
                        owner_id=r._mapping['owner_id'],
                        mail_raw=r._mapping['mail_raw'],
                    )
                    msgs.append(m)
                id_map = {m.id: m for m in msgs}
                ordered = [id_map[i] for i in ids if i in id_map]
                return ordered
        except Exception:
            # fall through to hosted retrieval
            pass

    # hosted embeddings retrieval (OpenAI or HuggingFace) or local model if available
    # ensure consistent indentation (previous error was due to mixed tabs/spaces)
    try:
        return await retrieve_similar_messages_hosted(
            query,
            group_id,
            since_days,
            top_k,
            session,
            owner_email=owner_email,
        )
    except Exception:
        # fallback: use retrieve_messages_for_group which performs explicit selects
        return await retrieve_messages_for_group(
            group_id,
            since_days,
            session,
            owner_email=owner_email,
        )


async def _cosine(a, b):
    # simple cosine similarity
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def _get_embeddings_bulk(texts: list):
    """Return list of embeddings for texts using OpenAI or HuggingFace inference API, or local SentenceTransformer if available.

    This function uses a small in-memory LRU cache to avoid repeated external calls for the same texts.
    """
    # check cache first
    results = [None] * len(texts)
    missing = []
    missing_idx = []
    for i, t in enumerate(texts):
        key = t or ''
        v = _cache_get(key)
        if v is not None:
            results[i] = v
        else:
            missing_idx.append(i)
            missing.append(key)

    if not missing:
        return results

    # fetch embeddings for missing texts
    fetched = None
    # Try OpenAI batch embeddings first, then fall back to HuggingFace, then local model
    if OPENAI_KEY:
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
            payload = {"model": OPENAI_EMBEDDING_MODEL, "input": missing}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                body = r.json()
                fetched = [d['embedding'] for d in body.get('data', [])]
        except Exception:
            # fall back to Hugging Face or local if available
            fetched = None
    if fetched is None and HUGGINGFACE_KEY:
        try:
            model = HUGGINGFACE_EMBEDDING_MODEL
            url = f"https://api-inference.huggingface.co/embeddings/{model}"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_KEY}"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, headers=headers, json={"input": missing})
                r.raise_for_status()
                body = r.json()
                if isinstance(body, dict) and 'embeddings' in body:
                    fetched = body['embeddings']
                elif isinstance(body, list) and all(isinstance(x, list) for x in body):
                    fetched = body
        except Exception:
            fetched = None
    if fetched is None and embedding_model is not None:
        vecs = embedding_model.encode(missing)
        fetched = [v.tolist() if hasattr(v, 'tolist') else list(v) for v in vecs]
    if fetched is None:
        raise RuntimeError('No embedding provider available')

    # if the provider returned a single embedding for all missing items, try to normalize
    if not isinstance(fetched, list):
        fetched = [fetched]

    # If lengths differ, fall back to best-effort mapping (pad/trim)
    if len(fetched) != len(missing):
        # if a single embedding returned, duplicate it (not ideal but safe)
        if len(fetched) == 1:
            fetched = [fetched[0]] * len(missing)
        else:
            # fallback: return cached ones only and raise for rest
            for idx in missing_idx:
                if results[idx] is None:
                    results[idx] = [0.0]
            return results

    # populate cache and results (simple mapping)
    for i, key in enumerate(missing):
        _cache_set(key, fetched[i])
    for j, idx in enumerate(missing_idx):
        results[idx] = fetched[j]

    return results


async def retrieve_similar_messages_hosted(query: str, group_id: int, since_days: int, top_k: int, session: AsyncSession, owner_email: Optional[str] = None):
    # get candidate messages (recent)
    since = datetime.utcnow() - timedelta(days=since_days)
    # select explicit columns to avoid referencing embedding column if it doesn't exist
    stmt = select(
        Message.id,
        Message.subject,
        Message.body,
        Message.sender,
        Message.recipient,
        Message.timestamp,
        Message.owner_id,
        Message.mail_raw,
    )
    if owner_email:
        stmt = stmt.where(Message.timestamp >= since, Message.recipient == owner_email)
    else:
        stmt = stmt.where(Message.timestamp >= since)
    stmt = stmt.order_by(Message.timestamp.desc()).limit(500)
    res = await session.execute(stmt)
    rows = res.fetchall()
    candidates = []
    for r in rows:
        m = Message(
            id=r._mapping['id'],
            subject=r._mapping['subject'],
            body=r._mapping['body'],
            sender=r._mapping['sender'],
            recipient=r._mapping['recipient'],
            timestamp=r._mapping['timestamp'],
            owner_id=r._mapping['owner_id'],
            mail_raw=r._mapping['mail_raw'],
        )
        candidates.append(m)
    if not candidates:
        return []
    # prepare texts with enhanced context
    texts = [f"Subject: {m.subject or 'No subject'}\nFrom: {m.sender}\n\n{m.body or ''}" for m in candidates]
    
    # compute embeddings for candidates and query in one batch
    try:
        embeddings = await _get_embeddings_bulk(texts + [query])
        query_emb = embeddings[-1]
        doc_embs = embeddings[:-1]
    except Exception:
        # fallback to keyword+recency scoring when embeddings provider is unavailable
        q = (query or '').lower()
        # basic significant tokens (length >=3)
        toks = [t for t in ''.join([c if c.isalnum() else ' ' for c in q]).split() if len(t) >= 3]
        want_latest = any(w in q for w in ["latest", "recent", "newest", "most recent", "new"])
        scored_kw = []
        for m in candidates:
            text = f"{m.subject or ''}\n{m.body or ''}".lower()
            kw_score = sum(text.count(t) for t in toks) if toks else 0
            # recency bonus: newer messages get higher score
            recency_bonus = 0.0
            try:
                # scale by position in the sorted-by-time list (already desc)
                idx = candidates.index(m)
                recency_bonus = max(0.0, (len(candidates) - idx) / len(candidates)) * (1.0 if want_latest else 0.3)
            except Exception:
                pass
            scored_kw.append((kw_score + recency_bonus, m))
        scored_kw.sort(key=lambda x: x[0], reverse=True)
        # if no keywords matched at all, just return most recent
        if scored_kw and scored_kw[0][0] == 0:
            return candidates[:top_k]
        return [m for s, m in scored_kw[:top_k]]

    # score docs with semantic similarity
    scored = []
    min_similarity = 0.3  # Minimum similarity threshold
    
    for m, emb in zip(candidates, doc_embs):
        sim = await _cosine(query_emb, emb)
        if sim >= min_similarity:  # Only include messages that are semantically relevant
            scored.append((sim, m))
    
    # Sort by similarity score
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Return top_k most relevant messages
    return [m for s, m in scored[:top_k]]

    try:
        vec = embedding_model.encode(query or '')
        vec_list = vec.tolist() if hasattr(vec, 'tolist') else list(vec)
        since = datetime.utcnow() - timedelta(days=since_days)
        # raw SQL using pgvector <-> operator for cosine/inner product depending on extension config
        sql = text("""
            SELECT id FROM messages
            WHERE timestamp >= :since
            ORDER BY embedding <-> :vec
            LIMIT :k
        """)
        res = await session.execute(sql, {'since': since, 'vec': vec_list, 'k': top_k})
        rows = res.fetchall()
        ids = [r[0] for r in rows]
        if not ids:
            return await retrieve_messages_for_group(group_id, since_days, session)
        q = await session.execute(select(Message).where(Message.id.in_(ids)))
        msgs = q.scalars().all()
        # preserve order by ids
        id_map = {m.id: m for m in msgs}
        ordered = [id_map[i] for i in ids if i in id_map]
        return ordered
    except Exception:
        return await retrieve_messages_for_group(group_id, since_days, session)
