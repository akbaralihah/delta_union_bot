from sqlalchemy import BIGINT, String
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Mapped, mapped_column, Session

from db.configs import engine, Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    lang: Mapped[str] = mapped_column(String, default="UZ")

    def __repr__(self):
        return f"<User id={self.id} tg={self.user_id} lang={self.lang}>"

    @classmethod
    def get_by_user_id(cls, user_id: int, session: Session):
        return session.query(cls).filter(cls.user_id == user_id).first()

    @classmethod
    def get_user_lang(cls, user_id: int, session: Session):
        user = session.query(User).filter(User.user_id == user_id).first()
        return user.lang if user else "UZ"

    @classmethod
    def update_user_lang(cls, user_id: int, new_lang: str, session: Session):
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.lang = new_lang
            session.commit()

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
