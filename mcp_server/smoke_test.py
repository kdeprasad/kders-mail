import asyncio
import json
import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import crud  # type: ignore
from mcp_server.db import AsyncSessionLocal  # type: ignore


async def run(query: str, recipient: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        msgs = await crud.retrieve_similar_messages(
            query=query,
            group_id=0,
            since_days=30,
            top_k=5,
            session=session,
            owner_email=recipient,
        )
    data = [{
        "id": m.id,
        "subject": m.subject,
        "sender": m.sender,
        "recipient": m.recipient,
        "timestamp": m.timestamp.isoformat() if m.timestamp else None,
        "preview": (m.body or "").strip()[:160]
    } for m in msgs]
    print(json.dumps({"items": data}, indent=2))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--recipient")
    args = p.parse_args()
    asyncio.run(run(args.query, args.recipient))
