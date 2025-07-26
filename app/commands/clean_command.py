"""
Clean command implementation for database maintenance.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.functions.database_operations import (
    clean_database,
    get_database_stats,
    vacuum_database,
)


class CleanCommand(BaseCommand):
    """Command for cleaning and maintaining the database."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the clean command."""
        try:
            # Get action from kwargs
            action = kwargs.get("action", "").lower()

            if not action:
                return {
                    "prompt": "action",
                    "message": "What would you like to do?",
                    "actions": [
                        {
                            "key": "clean",
                            "desc": "Clean database (drop all tables and recreate)",
                        },
                        {"key": "stats", "desc": "Show database statistics"},
                        {
                            "key": "vacuum",
                            "desc": "Vacuum database (optimize and reclaim space)",
                        },
                    ],
                }

            if action == "clean":
                result = clean_database()
                return CommandResult(True, result).to_dict()

            elif action == "stats":
                result = get_database_stats()
                return CommandResult(True, result).to_dict()

            elif action == "vacuum":
                result = vacuum_database()
                return CommandResult(True, result).to_dict()

            else:
                return CommandResult(
                    False,
                    f"Unknown action: {action}. Use 'clean', 'stats', or 'vacuum'",
                ).to_dict()

        except Exception as e:
            return CommandResult(False, f"Clean command failed: {str(e)}").to_dict()

    def get_help(self) -> str:
        return f"""
Clean Command Help
==================

The 'clean' command provides database maintenance operations.

Available Actions:
• clean  - Drop all tables and recreate schema (clears all data)
• stats  - Show database statistics and table information
• vacuum - Optimize database and reclaim unused space

Warning:
The 'clean' action will permanently delete all data including:
- User settings and API keys
- AI conversation history
- All session data

Usage:
- Type '/clean' and select an action
- Use with caution, especially the 'clean' action

Tip: Use 'stats' first to see what data you have before cleaning
        """
