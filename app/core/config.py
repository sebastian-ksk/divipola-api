from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://divipola_user:divipola_pass@localhost:5432/divipola_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    datos_gov_app_token: str = os.getenv("DATOS_GOV_APP_TOKEN", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()

