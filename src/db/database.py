from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    # echo=True,
)

session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
