from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    CHANNEL_ID: int
    ADMINS: List[int] = Field(default_factory=list)

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432

    CONTAINER_SHEET_URL: str
    CARGO_1_SHEET_URL: str
    CARGO_2_SHEET_URL: str
    GOOGLE_CREDENTIALS_PATH: str

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
