from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/subsurface"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRY: int = 3600
    REFRESH_TOKEN_EXPIRY: int = 604800


APP_SETTINGS = Settings()
