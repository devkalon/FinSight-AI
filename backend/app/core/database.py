import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import ssl as _ssl
from backend.app.core.config import settings

# Auto-correct driver: Neon/Render provide postgresql:// but asyncpg needs postgresql+asyncpg://
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg doesn't support sslmode= query param — strip it and use ssl connect_arg instead
_needs_ssl = "sslmode=" in _db_url
_db_url = _db_url.split("?")[0] if "postgresql" in _db_url and "?" in _db_url else _db_url

_connect_args: dict = {}
if "sqlite" in _db_url:
    _connect_args = {"check_same_thread": False}
elif _needs_ssl:
    _connect_args = {"ssl": _ssl.create_default_context()}

# Engine configuration
engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    poolclass=NullPool if "postgresql" in _db_url else None,
    connect_args=_connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
