"""
MCP Email Server (Option A):
- Standalone MCP server exposing your email data as tools.
- Intended to be run locally for developer/admin use (e.g., via Claude Desktop MCP).

Tools exposed:
- search_emails(query: str, recipient: Optional[str], limit: int = 5, since_days: int = 30)
- get_email_details(email_id: int)
- summarize_thread(thread_ids: List[int])  # basic merge + summary

Requires: `pip install -r mcp_server/requirements.txt`

Configure Claude Desktop (example ~/.claude/config.json):
{
  "mcpServers": {
    "emails": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MCP_DATABASE_URL": "postgresql+asyncpg://mailuser:mailpass@localhost:5432/maildb"
      }
    }
  }
}
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Reuse your backend models/CRUD
# Ensure Python can import the backend package when run from repo root
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP = ROOT / "backend" / "app"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND_APP.parent) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP.parent))

from backend.app import models  # noqa: E402
from backend.app import crud    # noqa: E402

from .db import AsyncSessionLocal

# Try to import the official MCP SDK
try:
    # The Python SDK exposes a high-level stdio server
    from mcp import Server, tool
except Exception as e:  # pragma: no cover
    print("This server requires the 'mcp' Python package. Install with:\n  pip install -r mcp_server/requirements.txt")
    raise


authenticated_recipient_env = os.getenv("MCP_DEFAULT_RECIPIENT")


async def _open_session() -> AsyncSession:
    return AsyncSessionLocal()


@tool(
    name="search_emails",
    description="Search user's emails by semantic/keyword query with recency awareness. Returns concise summaries.",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "recipient": {"type": "string", "description": "Limit results to this user/email (recommended). Optional if MCP_DEFAULT_RECIPIENT is set."},
            "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 25},
            "since_days": {"type": "integer", "default": 30, "minimum": 1, "maximum": 365}
        },
        "required": ["query"]
    }
)
async def search_emails(query: str, recipient: Optional[str] = None, limit: int = 5, since_days: int = 30) -> Dict[str, Any]:
    """Search relevant emails and return compact structured results."""
    owner_email = recipient or authenticated_recipient_env
    async with AsyncSessionLocal() as session:
        msgs = await crud.retrieve_similar_messages(
            query=query,
            group_id=0,
            since_days=since_days,
            top_k=limit,
            session=session,
            owner_email=owner_email,
        )
    results = []
    for m in msgs:
        results.append({
            "id": m.id,
            "subject": m.subject or "No subject",
            "sender": m.sender,
            "recipient": m.recipient,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "preview": (m.body or "").strip().splitlines()[0:3],
        })
    return {"items": results}


@tool(
    name="get_email_details",
    description="Fetch full content of a specific email by ID.",
    schema={
        "type": "object",
        "properties": {
            "email_id": {"type": "integer"}
        },
        "required": ["email_id"]
    }
)
async def get_email_details(email_id: int) -> Dict[str, Any]:
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(models.Message).where(models.Message.id == email_id)
        )
        msg = q.scalars().first()
        if not msg:
            return {"error": f"Email {email_id} not found"}
        return {
            "id": msg.id,
            "subject": msg.subject or "No subject",
            "sender": msg.sender,
            "recipient": msg.recipient,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            "body": msg.body,
        }


@tool(
    name="summarize_thread",
    description="Summarize a conversation thread by concatenating bodies in timestamp order.",
    schema={
        "type": "object",
        "properties": {
            "thread_ids": {"type": "array", "items": {"type": "integer"}}
        },
        "required": ["thread_ids"]
    }
)
async def summarize_thread(thread_ids: List[int]) -> Dict[str, Any]:
    if not thread_ids:
        return {"summary": "No messages provided."}
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(models.Message).where(models.Message.id.in_(thread_ids))
        )
        msgs = q.scalars().all()
    # Simple sort and naive summarization (first lines)
    msgs.sort(key=lambda m: m.timestamp or 0)
    lines: List[str] = []
    for m in msgs:
        lines.append(f"[{m.timestamp}] {m.sender} -> {m.recipient}: {m.subject or 'No subject'}")
        body_lines = (m.body or "").strip().splitlines()
        lines.extend(["  " + bl for bl in body_lines[:5]])
        lines.append("")
    # Let the LLM summarize text using client-side reasoning; return the compiled context
    return {"thread_context": "\n".join(lines)}


async def main() -> None:
    server = Server("emails")
    # Tools are registered by decorator; just run the stdio server
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
