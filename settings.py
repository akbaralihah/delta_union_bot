import os
from dotenv import load_dotenv

load_dotenv()


class Environment:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    CONTAINER_SHEET_URL = os.getenv("CONTAINER_SHEET_URL")
    CARGO_1_SHEET_URL = os.getenv("CARGO_1_SHEET_URL")
    CARGO_2_SHEET_URL = os.getenv("CARGO_2_SHEET_URL")
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

env = Environment()