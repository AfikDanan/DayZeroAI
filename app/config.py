from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    SENDGRID_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str = "google_credencial.json"
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str = ""  # For Render.com deployment

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Directories
    TEMP_DIR: str = "/tmp/preboarding"
    OUTPUT_DIR: str = "./videos"
    DEV_OUTPUT_DIR: str = "./dev_output"  # For development - saves intermediate files
    
    # Email Configuration
    FROM_EMAIL: str = "afikdanan@gmail.com"
    BASE_URL: str = "http://localhost:8000"
    
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Worker Settings
    WORKER_CONCURRENCY: int = 2
    JOB_TIMEOUT: int = 600  # 10 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()