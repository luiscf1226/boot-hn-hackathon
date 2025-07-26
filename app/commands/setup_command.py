"""
Setup command implementation for configuring Gemini model selection.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User, UserSettings
from app.core.config import settings
from app.utils.helpers import save_env_variable, validate_gemini_api_key, get_env_variable


class SetupCommand(BaseCommand):
    """Setup command for configuring the agent."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the setup command. Handles API key setup and model selection."""
        try:
            # Check if we're handling API key input
            api_key_input = kwargs.get("api_key")
            if api_key_input:
                return await self._handle_api_key_input(api_key_input)

            # Get API key from environment/settings
            api_key = get_env_variable("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here" or len(api_key.strip()) < 20:
                return {
                    "prompt": "api_key",
                    "message": "🔑 Gemini API Key Required",
                    "instructions": [
                        "Get your free API key from: https://makersuite.google.com/app/apikey",
                        "Copy the API key and paste it below",
                        "Your key will be saved securely to your .env file"
                    ],
                    "placeholder": "Paste your Gemini API key here..."
                }

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

    async def _handle_api_key_input(self, api_key: str) -> Dict[str, Any]:
        """Handle API key input, validation, and saving."""
        try:
            # Clean the input
            api_key = api_key.strip()

            # Validate API key format
            if not validate_gemini_api_key(api_key):
                return {
                    "prompt": "api_key",
                    "message": "❌ Invalid API Key Format",
                    "instructions": [
                        "Gemini API keys should start with 'AIza' and be around 39 characters long",
                        "Please check your key and try again",
                        "Get your key from: https://makersuite.google.com/app/apikey"
                    ],
                    "placeholder": "Paste your Gemini API key here...",
                    "error": "Invalid API key format"
                }

            # Save to .env file
            if save_env_variable("GEMINI_API_KEY", api_key):
                # Reload settings to pick up new API key
                from app.core.config import get_settings
                new_settings = get_settings()

                return CommandResult(True,
                    "✅ API key saved successfully! Now let's select your model...",
                    {"api_key_saved": True, "proceed_to_model": True}
                ).to_dict()
            else:
                return CommandResult(False,
                    "❌ Failed to save API key to .env file. Please check file permissions."
                ).to_dict()

        except Exception as e:
            return CommandResult(False, f"Error handling API key: {str(e)}").to_dict()

    def get_help(self) -> str:
        available_models = User.get_available_models()
        models_list = "\n     * ".join(available_models)
        return f"""
Setup Command Help
==================

The 'setup' command configures your AI model and API key.

🔑 API Key Setup:
     * You'll be prompted to enter your Gemini API key if not set
     * Get your free key from: https://makersuite.google.com/app/apikey
     * The key will be saved securely to your .env file

🤖 Available Models:
     * {models_list}

Usage: Just type '/setup' and follow the prompts!
        """
