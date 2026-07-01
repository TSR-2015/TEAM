import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "TeamBrain AI"
    APP_ENV: str = "development"
    PORT: int = 8000
    DEBUG: bool = True
    
    SECRET_KEY: str = "your-secret-key-here"
    
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_PERSONAL_ACCESS_TOKEN: str = ""
    
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
