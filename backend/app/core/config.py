from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

# Buscar .env en el root del proyecto (sube desde backend/app/core/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000

    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Google Gemini (tier gratuito - clasificador principal)
    gemini_api_key: str = ""

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "taricai-embeddings"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "taricai"
    postgres_user: str = "taricai"
    postgres_password: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # Railway / Production database URL (overrides individual postgres_* vars)
    database_url_override: str = Field(default="", alias="DATABASE_URL")

    @property
    def database_url(self) -> str:
        # Railway provides DATABASE_URL directly
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {
        "env_file": str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        "extra": "ignore",
        "populate_by_name": True,
    }


def _load_settings() -> Settings:
    """Carga settings, priorizando .env sobre variables de entorno vacias."""
    import os

    s = Settings()

    # Fix: si una env var del sistema esta vacia pero .env tiene valor,
    # recargar desde .env directamente (Claude Code pone ANTHROPIC_API_KEY='')
    if not s.anthropic_api_key and _ENV_FILE.exists():
        from dotenv import dotenv_values
        env_vals = dotenv_values(_ENV_FILE)
        if env_vals.get("ANTHROPIC_API_KEY"):
            s.anthropic_api_key = env_vals["ANTHROPIC_API_KEY"]

    return s


settings = _load_settings()
