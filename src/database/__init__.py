from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.core.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.timezone('Asia/Bishkek', func.now()),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.timezone('Asia/Bishkek', func.now()),
        onupdate=func.timezone('Asia/Bishkek', func.now())
    )


engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=5,
    max_overflow=4,
    pool_pre_ping=True,
    echo=settings.LOGGING_LEVEL == "DEBUG",
)
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
