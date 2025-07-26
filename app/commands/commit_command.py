"""
Commit command implementation for AI-generated git commit messages.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.services.agent import Agent
from app.commands.prompts import load_prompt, format_prompt
from app.functions.git_operations import (
    check_git_repository,
    get_staged_files,
    get_staged_diff,
    execute_git_commit,
    get_recent_commits
)


class CommitCommand(BaseCommand):
    """Command for generating AI commit messages and executing commits."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the commit command."""
        try:
            # Check if user wants to execute a commit
            action = kwargs.get("action", "").lower()
            commit_message = kwargs.get("commit_message", "")

            if action == "execute" and commit_message:
                # Execute the commit
                result = execute_git_commit(commit_message)
                return CommandResult(True, result, {"action": "executed"}).to_dict()

            # Check if it's a git repository
            repo_status = check_git_repository()
            if repo_status.startswith("❌"):
                return CommandResult(False, repo_status).to_dict()

            # Get staged files
            staged_files = get_staged_files()
            if staged_files.startswith("❌"):
                return CommandResult(False, staged_files).to_dict()

            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "❌ No API key found. Please run /setup first to configure your Gemini API key for AI commit message generation."
                ).to_dict()

            # Get staged diff for AI analysis
            staged_diff = get_staged_diff()
            if staged_diff.startswith("❌"):
                return CommandResult(False, staged_diff).to_dict()

            # Get recent commits for context
            recent_commits = get_recent_commits(3)

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session("Git Commit Message Generation")

            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Load AI prompts from files
            system_prompt = load_prompt("commit_system")
            user_message = format_prompt("commit_user", 
                                       staged_files=staged_files,
                                       staged_diff=staged_diff,
                                       recent_commits=recent_commits)

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI commit message generation failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Clean up the AI response (remove any extra formatting)
            commit_message = ai_response["response"].strip()

            # Remove quotes if AI added them
            if commit_message.startswith('"') and commit_message.endswith('"'):
                commit_message = commit_message[1:-1]
            if commit_message.startswith("'") and commit_message.endswith("'"):
                commit_message = commit_message[1:-1]

            # Return the generated commit message for user review
            return {
                "success": True,
                "message": "AI-generated commit message:",
                "commit_message": commit_message,
                "staged_files": staged_files,
                "prompt": "commit_confirm",
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown")
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Commit command failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    def get_help(self) -> str:
        return f"""
Commit Command Help
===================

The 'commit' command generates AI-powered git commit messages and executes commits.

How it works:
1. Checks if you're in a git repository
2. Analyzes staged files and changes
3. Uses AI to generate a professional commit message
4. Shows you the message and staged files
5. Lets you execute or cancel the commit

Prerequisites:
- Be in a git repository
- Have files staged for commit (use 'git add <files>')
- Set GEMINI_API_KEY in your .env file
- Run /setup to configure your AI model

Workflow:
1. Stage your files: git add <files>
2. Run: /commit
3. Review the AI-generated message
4. Choose to execute or cancel

The AI analyzes:
- What files changed
- The actual code changes (git diff)
- Recent commit history for context
- Follows git commit best practices

Note: Always review the generated message before committing!
        """
