"""
Review command implementation for AI-powered code review.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.services.agent import Agent
from app.functions.git_operations import (
    check_git_repository, 
    get_all_changes_diff,
    get_git_status,
    get_recent_commits
)


class ReviewCommand(BaseCommand):
    """Command for AI-powered code review of git changes."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the review command."""
        try:
            # Check if it's a git repository
            repo_status = check_git_repository()
            if repo_status.startswith("❌"):
                return CommandResult(False, repo_status).to_dict()
            
            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False, 
                    "❌ No API key found. Please run /setup first to configure your Gemini API key for AI code review."
                ).to_dict()
            
            # Get git status
            git_status = get_git_status()
            
            # Get changes diff for AI analysis
            changes_diff = get_all_changes_diff()
            if changes_diff.startswith("❌"):
                return CommandResult(False, changes_diff).to_dict()
            
            # Get recent commits for context
            recent_commits = get_recent_commits(3)
            
            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session("Code Review")
                
            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()
            
            # Create AI prompt for code review
            system_prompt = """You are a senior software engineer performing a code review. Analyze the git diff provided and provide constructive feedback.

Focus on:
1. **Code Quality**: Logic errors, edge cases, performance issues
2. **Security**: Potential vulnerabilities, input validation, authentication issues
3. **Best Practices**: Code style, naming conventions, architecture patterns
4. **Maintainability**: Code readability, documentation, complexity
5. **Testing**: Missing test cases, test coverage
6. **Dependencies**: New dependencies, version compatibility

Provide your review as a structured list of suggestions:

## 🔍 Code Review Findings

### ✅ Good Points
- List positive aspects of the changes

### ⚠️ Issues Found
- **[SEVERITY]** Description of issue
- **Location**: file:line
- **Suggestion**: How to fix

### 💡 Improvements
- Suggestions for enhancement
- Performance optimizations
- Better patterns to consider

### 🧪 Testing Recommendations
- Missing test scenarios
- Edge cases to consider

Be constructive and specific. Focus on actionable feedback."""

            user_message = f"""Please review these code changes:

GIT STATUS:
{git_status}

CODE CHANGES:
{changes_diff}

RECENT COMMITS (for context):
{recent_commits}

Provide a thorough code review with specific, actionable feedback."""

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )
                
                if not ai_response["success"]:
                    return CommandResult(False, f"AI code review failed: {ai_response.get('error', 'Unknown error')}").to_dict()
                    
            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()
            
            # Clean up the AI response
            review_content = ai_response["response"].strip()
            
            # Return the review results for user approval
            return {
                "success": True,
                "message": "🤖 AI Code Review Complete:",
                "review_content": review_content,
                "git_status": git_status,
                "prompt": "review_save_confirm",
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown")
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Review command failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    def get_help(self) -> str:
        return f"""
Review Command Help
===================

The 'review-changes' command provides AI-powered code review of your git changes.

🤖 How it works:
1. Checks if you're in a git repository
2. Analyzes all changes (staged and unstaged)
3. Uses AI to perform senior-level code review
4. Provides structured feedback and suggestions
5. Optionally saves review to database

📋 Prerequisites:
- Be in a git repository
- Have code changes (staged or unstaged)
- Set GEMINI_API_KEY in your .env file
- Run /setup to configure your AI model

🔄 Workflow:
1. Make your code changes
2. Run: /review-changes
3. Review the AI feedback
4. Choose to save review or continue

💡 The AI analyzes:
- Code quality and logic errors
- Security vulnerabilities
- Best practices and patterns
- Performance considerations
- Testing recommendations
- Maintainability issues

⚠️  Note: This is for defensive security analysis only!
        """