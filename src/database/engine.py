from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.database.models import Base
from src.config.settings import settings

_engine = None
_session_factory = None


def get_database_url() -> str:
    url = settings.DATABASE_URL
    if url:
        return url
    db_dir = Path("data")
    db_dir.mkdir(parents=True, exist_ok=True)
    return "sqlite+aiosqlite:///./data/shopagent.db"


def get_engine():
    global _engine
    if _engine is None:
        url = get_database_url()
        kwargs = {"poolclass": NullPool} if url.startswith("sqlite") else {}
        _engine = create_async_engine(url, **kwargs)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session():
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
