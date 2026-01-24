from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    APP_NAME: str = "Polyou API"
    DEBUG: bool = False

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

class FSRSConfig:
    #LEARNING
    LEARNING_MIN_STABILITY: float = 0.1
    LEARNING_STABILITY_INCREMENT: float = 2.0
    
    MINIMUM_REVIEW_INTERVAL: timedelta = timedelta(days=1)
    DESIRED_RETENTION: float = 0.95

DEFAULT_FSRS_CONFIG = FSRSConfig()
