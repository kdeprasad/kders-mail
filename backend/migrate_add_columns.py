"""
Migration script to add is_read and is_pinned columns to messages table
Run this on EC2: python migrate_add_columns.py
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate():
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@db:5432/maildb')
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        print("Adding is_read column...")
        try:
            await conn.execute(text(
                "ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE"
            ))
            print("✅ is_read column added")
        except Exception as e:
            print(f"⚠️  is_read column: {e}")
        
        print("Adding is_pinned column...")
        try:
            await conn.execute(text(
                "ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE"
            ))
            print("✅ is_pinned column added")
        except Exception as e:
            print(f"⚠️  is_pinned column: {e}")
        
        # Update existing rows to have default values
        print("Updating existing rows...")
        try:
            await conn.execute(text(
                "UPDATE messages SET is_read = FALSE WHERE is_read IS NULL"
            ))
            await conn.execute(text(
                "UPDATE messages SET is_pinned = FALSE WHERE is_pinned IS NULL"
            ))
            print("✅ Existing rows updated")
        except Exception as e:
            print(f"⚠️  Update: {e}")
    
    await engine.dispose()
    print("\n🎉 Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
