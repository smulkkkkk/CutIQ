from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    redis_url: str = "redis://localhost:6379"
    environment: str = "development"

    storage_bucket: str = "cutiq"

    whisper_model: str = "medium"
    whisper_device: str = "cpu"

settings = Settings()
