from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ─── Base de données ──────────────────────────────────────────────
    DATABASE_URL: str

    # ─── Redis ───────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── JWT ─────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES_BACHELIER: int = 1440
    ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN: int = 480

    # ─── LLM ─────────────────────────────────────────────────────────
    LLM_MODE: str = "cloud"
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ─── App ─────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()