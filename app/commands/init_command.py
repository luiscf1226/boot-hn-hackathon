"""
Init command implementation for project documentation generation.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.services.agent import Agent
from app.functions.project_analysis import get_project_summary
from app.functions.file_operations import create_file


class InitCommand(BaseCommand):
    """Command for initializing project documentation using AI."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the init command."""
        try:
            # Get project path from kwargs
            project_path = kwargs.get("project_path")

            if not project_path:
                return {
                    "prompt": "project_path",
                    "message": "Enter the project path to analyze:",
                    "placeholder": "Enter project path (or '.' for current directory)"
                }

            # Handle current directory
            if project_path.strip() in [".", "current", ""]:
                project_path = None  # Will use current directory

            # Check if user has API key configured first
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "No API key found. Please run /setup first to configure your Gemini API key.\n" +
                    "Get one from: https://makersuite.google.com/app/apikey"
                ).to_dict()

            # Get project summary
            try:
                project_summary = get_project_summary(project_path)

                if project_summary.startswith("Error"):
                    return CommandResult(False, project_summary).to_dict()

            except Exception as e:
                return CommandResult(False, f"Failed to analyze project: {str(e)}").to_dict()

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session("Project Documentation Generation")

            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Create AI prompt for documentation
            system_prompt = """You are a technical documentation expert. Based on the project analysis provided, create comprehensive documentation.

Create a professional README.md with:
- Project title and description
- Installation instructions
- Usage examples
- Project structure overview
- Contributing guidelines

Keep it concise but informative. Focus on making it useful for developers."""

            user_message = f"Please analyze this project and create a README.md:\n\n{project_summary[:2000]}..."  # Limit size

            # Send to AI with error handling
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI documentation generation failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Parse AI response and create files
            documentation_content = ai_response["response"]

            # Create README.md file
            try:
                readme_result = create_file(
                    file_path="README.md",
                    content=documentation_content,
                    project_root=project_path,
                    overwrite=True
                )

                if readme_result.startswith("Error"):
                    return CommandResult(False, f"Failed to create README.md: {readme_result}").to_dict()

            except Exception as e:
                return CommandResult(False, f"Failed to create README.md: {str(e)}").to_dict()

            # Create a project summary file
            try:
                summary_content = f"""# Project Analysis Summary

This file was generated automatically by the AI Coding Agent.

## Project Overview

{project_summary[:3000]}...

## AI Model Used
- Model: {ai_response.get('model', 'Unknown')}
- Session ID: {ai_response.get('session_id', 'Unknown')}

Generated on: {agent.current_session.created_at if agent.current_session else 'Unknown'}
"""

                summary_result = create_file(
                    file_path="PROJECT_ANALYSIS.md",
                    content=summary_content,
                    project_root=project_path,
                    overwrite=True
                )

            except Exception as e:
                summary_result = f"Error creating PROJECT_ANALYSIS.md: {str(e)}"

            result_message = f"Project documentation generated successfully!\n\n"
            result_message += f"Created README.md\n"
            result_message += f"Created PROJECT_ANALYSIS.md\n"
            result_message += f"Used AI model: {ai_response.get('model', 'Unknown')}\n"
            result_message += f"Conversation saved in session: {ai_response.get('session_id', 'Unknown')}\n"

            if summary_result.startswith("Error"):
                result_message += f"\nWarning: {summary_result}"

            return CommandResult(True, result_message, {
                "files_created": ["README.md", "PROJECT_ANALYSIS.md"],
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown"),
                "project_path": project_path or "current directory"
            }).to_dict()

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Init command failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    def get_help(self) -> str:
        return f"""
Init Command Help
=================

The 'init' command analyzes your project and generates comprehensive documentation using AI.

What it does:
- Analyzes project structure and files
- Identifies programming languages and frameworks
- Generates README.md with project overview
- Creates PROJECT_ANALYSIS.md with detailed analysis
- Uses AI to create professional documentation

Usage:
- Type '/init' and specify project path when prompted
- Use '.' for current directory
- Documentation will be created in the project root

AI Features:
- Uses your selected AI model
- Saves conversation in database
- Creates contextual documentation based on project type

Prerequisites:
- Set GEMINI_API_KEY in your .env file
- Run /setup to configure your AI model
        """
