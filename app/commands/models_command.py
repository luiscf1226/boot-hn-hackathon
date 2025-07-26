"""
Models command implementation for viewing and changing AI models.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.core.config import settings


class ModelsCommand(BaseCommand):
    """Command for viewing and changing AI models."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the models command."""
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
            
            # Get model from kwargs (if user wants to change)
            new_model = kwargs.get("model")
            available_models = User.get_available_models()

            if not new_model:
                # Just show current model and available options
                current_model = user.selected_model if user.selected_model else "gemini-2.0-flash-exp"
                return {
                    "prompt": "model",
                    "message": f"Current model: {current_model}\n\nAvailable models:",
                    "available_models": available_models,
                    "current_model": current_model
                }

            # Validate new model
            if new_model not in available_models:
                return {
                    "prompt": "model",
                    "message": f"Model '{new_model}' is not valid. Choose from the list:",
                    "available_models": available_models,
                    "current_model": user.selected_model if user.selected_model else "gemini-2.0-flash-exp"
                }

            # Update the model
            success = user.update_configuration(self.db, api_key, new_model)
            if success:
                return CommandResult(True,
                    f"✅ Model changed to: {new_model}",
                    {"model": new_model, "previous_model": user.selected_model}
                ).to_dict()
            else:
                return CommandResult(False, "Failed to update model").to_dict()

        except Exception as e:
            return CommandResult(False, f"Models command failed: {str(e)}").to_dict()

    def get_help(self) -> str:
        available_models = User.get_available_models()
        models_list = "\n     * ".join(available_models)
        return f"""
Models Command Help
===================

The 'models' command shows your current AI model and allows you to change it.

🤖 Available Models:
     * {models_list}

Usage: 
- Type '/models' to see current model and options
- Select a number to change to that model

Prerequisites:
- Set GEMINI_API_KEY in your .env file
- Get API key from: https://makersuite.google.com/app/apikey
        """