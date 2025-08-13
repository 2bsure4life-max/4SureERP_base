from typing import List
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "4SureERP Base"
    APP_VERSION: str = "0.1.0"
    DB_URL: str
    JWT_SIGNING_KEY: str
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_TOKEN_MINUTES: int = 60*24*30
    CORS_ALLOW_ORIGINS: str = ""

    @property
    def cors_origins(self) -> List[str]:
        raw = self.CORS_ALLOW_ORIGINS.strip()
        return [o.strip() for o in raw.split(",") if o.strip()]

settings = Settings(_env_file=os.path.join(os.path.dirname(__file__), ".env"))
