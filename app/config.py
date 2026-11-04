from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://student_Philipp-spring-events-aggregator-postgres:REDACTED@postgres-postgresql.postgres.svc:5432/student_Philipp-spring-events-aggregator-postgres"

    api_key: str = "YOUR_API_KEY"

    api_base_url: str = "https://events-provider.dev-2.python-labs.ru"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
