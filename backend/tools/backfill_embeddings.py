import asyncio
import os
from sqlalchemy import select

from app.database import async_session, engine
from app.models import Message

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


async def backfill(batch_size: int = 50):
    if SentenceTransformer is None:
        print("sentence-transformers not available in this environment. Aborting backfill.")
        return

    model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    print(f"Loading embedding model {model_name}...")
    model = SentenceTransformer(model_name)

    async with async_session() as session:
        # count messages without embedding
        q = await session.execute(select(Message).where(Message.embedding == None).limit(1))
        first = q.scalars().first()
        if not first:
            print("No messages without embeddings found.")
            return

        offset = 0
        while True:
            q = await session.execute(select(Message).where(Message.embedding == None).limit(batch_size).offset(offset))
            msgs = q.scalars().all()
            if not msgs:
                break
            print(f"Processing batch of {len(msgs)} messages (offset {offset})")
            texts = [m.body or '' for m in msgs]
            vecs = model.encode(texts)
            for m, v in zip(msgs, vecs):
                try:
                    m.embedding = v.tolist() if hasattr(v, 'tolist') else list(v)
                    session.add(m)
                except Exception as e:
                    print(f"Failed to set embedding for message {m.id}: {e}")
            await session.commit()
            offset += batch_size

    print("Backfill complete.")


if __name__ == '__main__':
    asyncio.run(backfill())
