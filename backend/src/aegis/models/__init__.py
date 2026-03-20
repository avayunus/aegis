"""AEGIS database models and initialization.

Uses SQLAlchemy 2.0 async with aiosqlite for the MVP.
Tables are created on startup via init_db().
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from aegis.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def init_db() -> None:
    """Create all database tables.

    Called once during application startup (see main.py lifespan).
    """
    from aegis.models import mission, asset, command, audit  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Tables initialized")


async def get_session() -> AsyncSession:
    """Dependency for FastAPI endpoints that need DB access."""
    async with async_session() as session:
        yield session
