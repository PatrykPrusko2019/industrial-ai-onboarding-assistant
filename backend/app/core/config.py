from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Industrial AI Onboarding Assistant"
    environment: str = "development"

    database_url: str = (
        "postgresql://industrial_ai_user:industrial_ai_password"
        "@localhost:5433/industrial_ai_db"
    )

    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()