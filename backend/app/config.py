from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = Field(default="dev-secret-change-me")
    fernet_key: str = Field(default="")
    database_url: str = Field(default="sqlite:///./auto_trader.db")
    access_token_expire_minutes: int = Field(default=60 * 24)
    cors_origins: str = Field(default="http://localhost:3000")
    scheduler_enabled: bool = Field(default=True)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
