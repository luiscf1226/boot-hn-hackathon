"""
User model for storing user settings and API configuration.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from app.core.database import Base


class User(Base):
    """User model for storing user configuration."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, default="default_user")

    # Gemini API configuration
    gemini_api_key = Column(Text, nullable=True)
    selected_model = Column(String(100), nullable=True)

    # Settings
    is_configured = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(username={self.username}, configured={self.is_configured})>"

    @classmethod
    def get_or_create_default_user(cls, db: Session) -> 'User':
        """Get existing default user or create one."""
        user = db.query(cls).filter(cls.username == "default_user").first()

        if not user:
            user = cls(username="default_user")
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create default settings
            settings = UserSettings(user_id=user.id)
            db.add(settings)
            db.commit()

        return user

    @classmethod
    def get_default_user(cls, db: Session) -> Optional['User']:
        """Get the default user if exists."""
        return db.query(cls).filter(cls.username == "default_user").first()

    def is_setup_complete(self) -> bool:
        """Check if user setup is complete."""
        return self.is_configured and self.gemini_api_key and self.selected_model

    def get_masked_api_key(self) -> str:
        """Get masked API key for display."""
        if not self.gemini_api_key:
            return "Not set"
        if len(self.gemini_api_key) <= 4:
            return "*" * len(self.gemini_api_key)
        return "*" * (len(self.gemini_api_key) - 4) + self.gemini_api_key[-4:]

    def update_configuration(self, db: Session, api_key: str, model: str) -> bool:
        """Update user configuration with API key and model."""
        try:
            self.gemini_api_key = api_key
            self.selected_model = model
            self.is_configured = True

            db.commit()
            return True

        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            db.rollback()
            return False

    def get_configuration_summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            "username": self.username,
            "is_configured": self.is_configured,
            "api_key_set": bool(self.gemini_api_key),
            "api_key_masked": self.get_masked_api_key(),
            "model": self.selected_model,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def validate_api_key(cls, api_key: str) -> Tuple[bool, str]:
        """Validate API key format."""
        if not api_key:
            return False, "API key is required!"

        if len(api_key) < 10:
            return False, "API key seems too short. Please check and try again."

        # Add more validation rules as needed
        return True, "API key is valid"

    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available Gemini models."""
        return [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro"
        ]

    @classmethod
    def validate_model_choice(cls, choice: str) -> Tuple[bool, Optional[str], str]:
        """Validate model choice and return model name."""
        available_models = cls.get_available_models()

        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_models):
                selected_model = available_models[choice_num - 1]
                return True, selected_model, f"Selected: {selected_model}"
            else:
                return False, None, f"Please enter a number between 1 and {len(available_models)}"
        else:
            return False, None, "Please enter a valid number"


class UserSettings(Base):
    """Additional user settings and preferences."""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)  # Default user ID

    # AI settings
    temperature = Column(String(10), default="0.7")
    max_tokens = Column(Integer, default=2048)

    # Agent preferences
    auto_commit = Column(Boolean, default=False)
    verbose_mode = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, temp={self.temperature})>"

    @classmethod
    def get_or_create_for_user(cls, db: Session, user_id: int) -> 'UserSettings':
        """Get or create settings for a user."""
        settings = db.query(cls).filter(cls.user_id == user_id).first()

        if not settings:
            settings = cls(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return settings

    def update_settings(self, db: Session, **kwargs) -> bool:
        """Update user settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            db.commit()
            return True

        except Exception as e:
            print(f"❌ Error updating settings: {e}")
            db.rollback()
            return False
