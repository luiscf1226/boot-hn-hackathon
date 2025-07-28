"""
Application configuration management.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    app_name: str = Field(default="AI Coding Agent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")

    # Database settings
    database_url: str = Field(default=None, env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.database_url is None:
            # Create boot-hn/temp/db directory in user's home
            home_dir = Path.home()
            db_dir = home_dir / "boot-hn" / "temp" / "db"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.database_url = f"sqlite:///{db_dir}/app.db"

    # AI settings
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")

    # Security settings
    secret_key: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get settings instance lazily."""
    return Settings()


# For backwards compatibility - but use get_settings() instead
_settings_instance = None


def _get_settings_cached():
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# Alias for backwards compatibility
settings = type(
    "SettingsProxy",
    (),
    {"__getattr__": lambda self, name: getattr(_get_settings_cached(), name)},
)()
