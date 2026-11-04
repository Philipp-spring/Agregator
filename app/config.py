import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aggregator_db"
    api_key: str = "YOUR_API_KEY"
    
    api_base_url: str = os.getenv("API_BASE_URL", "http://postgres.svc")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

