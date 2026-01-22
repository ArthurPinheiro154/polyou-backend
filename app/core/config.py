from pydantic_settings import BaseSettings

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