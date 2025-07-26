"""
Setup command implementation for configuring Gemini API and model selection.
"""

import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User, UserSettings


class SetupCommand(BaseCommand):
    """Setup command for configuring the agent."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the setup command."""
        try:
            print("\n🤖 Welcome to Agent Setup!")
            print("=" * 50)

            # Get or create user
            user = User.get_or_create_default_user(self.db)

            # Check if already configured
            if user.is_setup_complete():
                print(f"\n✅ Agent is already configured!")
                print(f"📍 Current API Key: {user.get_masked_api_key()}")
                print(f"🤖 Current Model: {user.selected_model}")

                reconfigure = input("\n🔄 Do you want to reconfigure? (y/N): ").strip().lower()
                if reconfigure not in ['y', 'yes']:
                    return CommandResult(True, "Setup cancelled by user").to_dict()

            # Get API key
            api_key = await self._prompt_for_api_key(user.gemini_api_key)
            if not api_key:
                return CommandResult(False, "Setup cancelled - API key is required").to_dict()

            # Get model selection
            selected_model = await self._prompt_for_model(user.selected_model)
            if not selected_model:
                return CommandResult(False, "Setup cancelled - Model selection is required").to_dict()

            # Save configuration using User model method
            success = user.update_configuration(self.db, api_key, selected_model)

            if success:
                config_summary = user.get_configuration_summary()
                print("\n✅ Setup completed successfully!")
                print(f"🔑 API Key: {config_summary['api_key_masked']}")
                print(f"🤖 Selected Model: {config_summary['model']}")

                return CommandResult(True, "Setup completed successfully", {
                    "api_key_set": config_summary['api_key_set'],
                    "model": config_summary['model']
                }).to_dict()
            else:
                return CommandResult(False, "Failed to save configuration").to_dict()

        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            return CommandResult(False, "Setup cancelled by user").to_dict()
        except Exception as e:
            print(f"\n❌ Error during setup: {str(e)}")
            return CommandResult(False, f"Setup failed: {str(e)}").to_dict()

    async def _prompt_for_api_key(self, current_key: str = None) -> str:
        """Prompt user for Gemini API key."""
        print("\n🔑 Gemini API Key Configuration")
        print("-" * 35)

        if current_key:
            masked_key = User(gemini_api_key=current_key).get_masked_api_key()
            print(f"Current API Key: {masked_key}")
            print("Press Enter to keep current key, or enter a new one:")
        else:
            print("Please enter your Gemini API key:")
            print("(You can get one from: https://makersuite.google.com/app/apikey)")

        while True:
            try:
                api_key = input("\n🔑 API Key: ").strip()

                # If no input and we have current key, keep it
                if not api_key and current_key:
                    return current_key

                # Validate API key using User model method
                is_valid, message = User.validate_api_key(api_key)
                if is_valid:
                    return api_key
                else:
                    print(f"❌ {message}")
                    continue

            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    async def _prompt_for_model(self, current_model: str = None) -> str:
        """Prompt user to select a Gemini model."""
        print("\n🤖 Model Selection")
        print("-" * 20)
        print("Available Gemini models:")

        available_models = User.get_available_models()

        for i, model in enumerate(available_models, 1):
            current_marker = " (current)" if model == current_model else ""
            print(f"  {i}. {model}{current_marker}")

        if current_model:
            print(f"\nCurrent model: {current_model}")
            print("Enter number to select a model, or press Enter to keep current:")
        else:
            print("\nEnter the number of your choice:")

        while True:
            try:
                choice = input("\n🤖 Model choice: ").strip()

                # If no input and we have current model, keep it
                if not choice and current_model:
                    return current_model

                # Validate choice using User model method
                is_valid, selected_model, message = User.validate_model_choice(choice)
                if is_valid:
                    print(f"✅ {message}")
                    return selected_model
                elif not choice:
                    print("❌ Model selection is required!")
                    continue
                else:
                    print(f"❌ {message}")
                    continue

            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    def get_help(self) -> str:
        """Get help text for the setup command."""
        available_models = User.get_available_models()
        models_list = "\n     * ".join(available_models)

        return f"""
Setup Command Help
==================

The 'setup' command configures your AI coding agent with:

1. 🔑 Gemini API Key
   - Required for AI functionality
   - Get one from: https://makersuite.google.com/app/apikey
   - Stored securely in local SQLite database

2. 🤖 Model Selection
   - Choose from available Gemini models:
     * {models_list}

Usage: Just type 'setup' and follow the prompts!

The setup will guide you through each step and save your preferences locally.
You can run setup again anytime to change your configuration.
        """
