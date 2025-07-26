"""
Setup command implementation for configuring Gemini model selection.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User, UserSettings
from app.core.config import settings


class SetupCommand(BaseCommand):
    """Setup command for configuring the agent."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the setup command. Only asks for model selection."""
        try:
            # Get API key from settings
            api_key = settings.gemini_api_key
            if not api_key or api_key == "your_gemini_api_key_here":
                return CommandResult(False,
                    "Please set GEMINI_API_KEY in your .env file\n" +
                    "Get one from: https://makersuite.google.com/app/apikey"
                ).to_dict()

            # Get or create user
            user = User.get_or_create_default_user(self.db)

            # Get model from kwargs or prompt
            model = kwargs.get("model")
            available_models = User.get_available_models()

            if not model:
                return {
                    "prompt": "model",
                    "message": "Select a Gemini model:",
                    "available_models": available_models,
                    "current_model": user.selected_model if user.selected_model else "gemini-2.0-flash-exp"
                }

            # Validate model
            if model not in available_models:
                return {
                    "prompt": "model",
                    "message": f"Model '{model}' is not valid. Choose from the list:",
                    "available_models": available_models,
                    "current_model": user.selected_model if user.selected_model else "gemini-2.0-flash-exp"
                }

            # Save configuration
            success = user.update_configuration(self.db, api_key, model)
            if success:
                return CommandResult(True,
                    f"✅ Setup completed! Using model: {model}",
                    {"model": model, "api_key_set": True}
                ).to_dict()
            else:
                return CommandResult(False, "Failed to save configuration").to_dict()

        except Exception as e:
            return CommandResult(False, f"Setup failed: {str(e)}").to_dict()

    def get_help(self) -> str:
        available_models = User.get_available_models()
        models_list = "\n     * ".join(available_models)
        return f"""
Setup Command Help
==================

The 'setup' command configures your AI model selection.

🤖 Available Models:
     * {models_list}

Prerequisites:
- Set GEMINI_API_KEY in your .env file
- Get API key from: https://makersuite.google.com/app/apikey

Usage: Just type '/setup' and select your preferred model!
        """
