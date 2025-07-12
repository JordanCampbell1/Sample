# import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# DATABASE_URL = os.getenv("DATABASE_URL")
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
# REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


class Settings(BaseSettings):
    DATABASE_URL: str  # = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str  # = os.getenv("SECRET_KEY", "")
    ALGORITHM: str  # = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: (
        int  # = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int  # = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
