from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


APP_SETTINGS = Settings()
