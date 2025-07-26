"""
Unknown command implementation for handling unrecognized user input with AI.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.services.agent import Agent


class UnknownCommand(BaseCommand):
    """Command for handling unknown/unrecognized user input via AI."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, text: str = "", **kwargs) -> Dict[str, Any]:
        """Execute the unknown command by calling AI to respond to user input."""
        try:
            if not text.strip():
                return CommandResult(False, "No input provided").to_dict()

            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "I'd love to help, but I need an API key configured first. Please run /setup to configure your Gemini API key so I can assist you!"
                ).to_dict()

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session("General Assistant")
            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Create system prompt for the CLI agent
            system_prompt = """You are Boot-hn, a helpful CLI coding agent and assistant. A user has typed something that doesn't match any of the available commands, so you should respond helpfully and guide them.

AVAILABLE COMMANDS:
• /setup - Configure AI model and API key
• /models - Display and change AI models
• /init - Initialize project documentation
• /review-changes - Review git changes with AI
• /explain - Explain code from files or paste
• /commit - Generate AI commit messages
• /clean - Database maintenance (clean/stats/vacuum)
• /clear - Clear terminal output

Your role:
1. **Be helpful and friendly** - You're an AI coding assistant
2. **Understand intent** - Try to figure out what the user wants to do
3. **Guide to correct commands** - Suggest the right command for their needs
4. **Provide assistance** - If they have coding questions, help them out
5. **Be conversational** - You can chat and be personable

Response style:
- Keep responses concise but helpful
- Use a friendly, professional tone
- Include relevant command suggestions when appropriate
- If they're asking about code/programming, provide helpful answers
- Always end with a suggestion for the most relevant command they should try

Remember: You are a CLI agent helping users with coding tasks. Be practical and guide them toward using the available commands when appropriate."""

            user_message = f"""User typed: "{text}"

Please respond helpfully to this user input. If it seems like they want to use a specific feature, guide them to the right command. If they're asking a general question, answer it and suggest relevant commands."""

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI assistant failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Clean up the AI response
            assistant_response = ai_response["response"].strip()

            # Return the AI response
            return {
                "success": True,
                "message": "Boot-hn Assistant:",
                "assistant_response": assistant_response,
                "user_input": text,
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown"),
                "response_type": "ai_assistant"
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Assistant failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    def get_help(self) -> str:
        """Get help text for the unknown command."""
        return """Unknown Command Handler
======================

This command handles unrecognized input by using AI to provide helpful responses.

How it works:
1. When you type something that isn't a recognized command
2. The AI assistant analyzes your input
3. Provides helpful responses and guidance
4. Suggests the most appropriate commands to use

The AI can help with:
- General coding questions
- Guidance on which command to use
- Explanations of features
- Friendly conversation about development

Available Commands:
/setup - Configure AI model and API key
/models - Display and change AI models
/init - Initialize project documentation
/review-changes - Review git changes with AI
/explain - Explain code from files or paste
/commit - Generate AI commit messages
/clean - Database maintenance
/clear - Clear terminal output

Prerequisites:
- Set GEMINI_API_KEY in your .env file
- Run /setup to configure your AI model

Examples of things you can type:
"How do I analyze my code?"
"What does this project do?"
"Help me understand git commits"
"I want to document my project"

The AI will understand your intent and guide you to the right command!"""
