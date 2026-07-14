from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # Application
    # ==========================
    APP_NAME: str
    APP_VERSION: str
    API_PREFIX: str

    DEBUG: bool
    HOST: str
    PORT: int

    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # ==========================
    # Security
    # ==========================
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ========================
    # GOOGLE_API_KEY
    # ========================
    GOOGLE_API_KEY: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()