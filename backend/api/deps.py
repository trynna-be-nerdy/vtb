from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import async_session as AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
