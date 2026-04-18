"""
RegRadar Configuration Module

Loads settings from environment variables with secure defaults.
Never hardcodes secrets - all API keys loaded from .env
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"
    debug: bool = True

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # Database
    database_url: str = "sqlite:///./regradar.db"

    # AI (Gemini)
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_timeout_seconds: int = 30

    # Scraper Configuration
    scraper_enabled: bool = True
    scraper_interval_hours: int = 6
    request_timeout_seconds: int = 30
    rate_limit_delay_seconds: float = 2.0

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Sentry (Error Tracking)
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"

    # Email (Phase 2)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: str = "noreply@regradar.com"

    # Security
    api_key_scraper: str
    cors_origins: str = "http://localhost:3000"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
