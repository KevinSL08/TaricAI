from pathlib import Path

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

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {
        "env_file": str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        "extra": "ignore",
    }


settings = Settings()
