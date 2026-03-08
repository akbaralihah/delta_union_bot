from typing import List, Optional
from sqlalchemy import BIGINT, String, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from db.configs import Base, redis_client


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    lang: Mapped[str] = mapped_column(String, default="UZ")

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.user_id} lang={self.lang}>"

    @classmethod
    async def get_by_user_id(cls, user_id: int, session: AsyncSession) -> Optional["User"]:
        stmt = select(cls).where(cls.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_lang(cls, user_id: int, session: AsyncSession) -> str:
        cache_key = f"user:lang:{user_id}"
        # get lang from cache
        cached_lang = await redis_client.get(cache_key)
        if cached_lang:
            return cached_lang

        # if lang not found in cache
        stmt = select(cls.lang).where(cls.user_id == user_id)
        result = await session.execute(stmt)
        lang = result.scalar_one_or_none() or "UZ"

        # save found lang to cache
        await redis_client.setex(cache_key, 86400, lang)

        return lang

    @classmethod
    async def update_user_lang(cls, user_id: int, new_lang: str, session: AsyncSession) -> None:
        stmt = update(cls).where(cls.user_id == user_id).values(lang=new_lang)
        await session.execute(stmt)
        await session.commit()

        # add lang to cache
        cache_key = f"user:lang:{user_id}"
        await redis_client.setex(cache_key, 86400, new_lang)

    @classmethod
    async def upsert(cls, session: AsyncSession, user_id: int, full_name: str, username: Optional[str]) -> None:
        stmt = pg_insert(cls).values(
            user_id=user_id,
            full_name=full_name,
            username=username
        ).on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "full_name": full_name,
                "username": username
            }
        )
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_all_user_ids(cls, session: AsyncSession) -> List[int]:
        stmt = select(cls.user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
