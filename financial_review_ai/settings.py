from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    change_threshold: float = 0.3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

