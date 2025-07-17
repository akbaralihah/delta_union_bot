from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from db.configs import engine, Base

engine.connect()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(__type_pos=BIGINT, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    # todo
