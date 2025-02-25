from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vendor_shop.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key-replace-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

# Configure logging
def setup_logging():
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Create logger instance
    logger = logging.getLogger(__name__)
    return logger

# Initialize logger
logger = setup_logging()