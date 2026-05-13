from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_min_size,
    max_overflow=settings.db_pool_max_overflow,
    # Detect and recycle stale connections before handing them to a handler
    pool_pre_ping=True,
    # Recycle connections after 1 hour to avoid hitting Postgres idle timeouts
    pool_recycle=3600,
    echo=False,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)
