from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

def get_async_database_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy"""
    if url and "postgresql://" in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url

async_db_url = get_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    async_db_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
