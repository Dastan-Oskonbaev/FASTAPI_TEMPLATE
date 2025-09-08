from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

Base = declarative_base()
engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=5,
    max_overflow=4,
    # pool_pre_ping=True,
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
