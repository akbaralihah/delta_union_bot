from sqlalchemy import BIGINT, select, String
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Mapped, mapped_column

from db.configs import engine, Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)

    @classmethod
    def upsert(cls, session, user_id: int, full_name: str, username: str | None):
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
        session.execute(stmt)
        session.commit()

    @classmethod
    def get_all_user_ids(cls, session):
        return [row[0] for row in session.query(cls.user_id).all()]


Base.metadata.create_all(engine)
