from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from redis.asyncio import Redis

from settings import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.db_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
