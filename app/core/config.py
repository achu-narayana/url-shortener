from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DATABASE_URL: str
    REDIS_URL: str
    FRONTEND_URL: str = "http://localhost:5500"
    SHORT_CODE_LENGTH: int = 7
    BASE_URL: str = "http://localhost:8000"
    CACHE_TTL_SECONDS: int = 3600


settings = Settings()
