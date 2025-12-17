"""
Configuration settings for SubScout backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SubScout"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://subscout.app"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://subscout:password@localhost:5432/subscout_db"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis (for queue and caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 50
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:3000/auth/callback"
    )
    
    # Gmail API
    GMAIL_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    GMAIL_API_QUOTA_PER_USER: int = 250  # Per second
    GMAIL_BATCH_SIZE: int = 500  # Emails per batch
    
    # LLM / AI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_PROVIDER: str = "openai"  # openai or anthropic
    LLM_MODEL: str = "gpt-4"  # or claude-3-5-sonnet-20241022
    LLM_TEMPERATURE: float = 0.1  # Low for consistent extraction
    LLM_MAX_TOKENS: int = 1000
    
    # Detection
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.5
    RULE_BASED_FIRST: bool = True  # Try rules before LLM
    
    # Unsubscribe
    UNSUBSCRIBE_TIMEOUT_SECONDS: int = 30
    UNSUBSCRIBE_MAX_RETRIES: int = 3
    CONFIRMATION_MONITORING_DAYS: int = 7
    
    # Email scanning
    DEFAULT_SCAN_YEARS: int = 3
    EMAIL_SEARCH_QUERY: str = (
        "category:updates OR category:promotions "
        "(subscription OR billing OR renew OR payment OR invoice OR receipt)"
    )
    
    # Encryption (for refresh tokens)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # 32-byte key for Fernet
    
    # Celery (background workers)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Rate limiting
    RATE_LIMIT_PER_USER: int = 100  # requests per minute
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Security
    CORS_ALLOW_CREDENTIALS: bool = True
    SECURE_COOKIES: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """Validate that all critical settings are configured"""
    errors = []
    
    if not settings.GOOGLE_CLIENT_ID:
        errors.append("GOOGLE_CLIENT_ID is not set")
    
    if not settings.GOOGLE_CLIENT_SECRET:
        errors.append("GOOGLE_CLIENT_SECRET is not set")
    
    if not settings.JWT_SECRET_KEY or settings.JWT_SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("JWT_SECRET_KEY must be set to a secure random value")
    
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        errors.append("Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be set")
    
    if not settings.ENCRYPTION_KEY:
        errors.append("ENCRYPTION_KEY must be set for token encryption")
    
    if errors:
        error_msg = "\n".join(errors)
        raise ValueError(f"Configuration errors:\n{error_msg}")


# Run validation
if settings.ENVIRONMENT == "production":
    validate_settings()
