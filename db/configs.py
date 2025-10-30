import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from settings import env

Base = declarative_base()

DB_CONFIG = f"postgresql+psycopg2://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"

engine = create_engine(DB_CONFIG)
session = Session(engine)
