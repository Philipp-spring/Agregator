import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USERNAME', 'postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DATABASE_NAME', 'aggregator_db')}"
    )

    api_key: str = "YOUR_API_KEY"
    api_base_url: str = "http://student-system-events-provider-web.student-system-events-provider.svc:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
