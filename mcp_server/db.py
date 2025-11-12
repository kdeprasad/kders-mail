import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Use a dedicated env var for local MCP server; fall back to localhost defaults
MCP_DATABASE_URL = os.getenv(
    "MCP_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://mailuser:mailpass@localhost:5432/maildb",
    ),
)

engine = create_async_engine(MCP_DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
