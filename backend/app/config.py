from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "backend/.env"), extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://worksync:worksync@localhost:5432/worksync"
    REDIS_URL: str = "redis://localhost:6380/0"
    MEILI_URL: str = "http://localhost:7700"
    MEILI_KEY: str = ""
    JWT_SECRET: str = Field(default="change-this-development-secret", min_length=16)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:3000"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    SITE_URL: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
