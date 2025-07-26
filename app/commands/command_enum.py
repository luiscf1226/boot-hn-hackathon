"""
Command enumeration for the AI Coding Agent.
Defines all available commands that the agent can execute.
"""

from enum import Enum
from typing import Dict, List


class AgentCommand(Enum):
    """Enumeration of all available agent commands."""

    # Core workflow commands
    SETUP = "setup"
    MODELS = "models"
    INIT = "init"
    REVIEW_CHANGES = "review-changes"
    EXPLAIN = "explain"
    COMMIT = "commit"
    CLEAN = "clean"


class CommandInfo:
    """Information about a command."""

    def __init__(self, command: AgentCommand, description: str, category: str):
        self.command = command
        self.description = description
        self.category = category


# Command descriptions and categories
COMMAND_INFO: Dict[AgentCommand, CommandInfo] = {
    # Development workflow commands
    AgentCommand.SETUP: CommandInfo(
        AgentCommand.SETUP,
        "Configure the agent settings and preferences",
        "Agent Configuration"
    ),
    AgentCommand.MODELS: CommandInfo(
        AgentCommand.MODELS,
        "Display database models and their relationships",
        "Database Operations"
    ),
    AgentCommand.INIT: CommandInfo(
        AgentCommand.INIT,
        "Create project documentation, README, and save context",
        "Project Initialization"
    ),
    AgentCommand.REVIEW_CHANGES: CommandInfo(
        AgentCommand.REVIEW_CHANGES,
        "Get git diff and perform code review analysis",
        "Code Review"
    ),
    AgentCommand.EXPLAIN: CommandInfo(
        AgentCommand.EXPLAIN,
        "Explain code from file or pasted content",
        "Code Analysis"
    ),
    AgentCommand.COMMIT: CommandInfo(
        AgentCommand.COMMIT,
        "Generate intelligent commit messages based on changes",
        "Version Control"
    ),
    AgentCommand.CLEAN: CommandInfo(
        AgentCommand.CLEAN,
        "Delete SQLite database and clean up temporary files",
        "Maintenance"
    ),
}


def get_commands_by_category() -> Dict[str, List[CommandInfo]]:
    """Get commands organized by category."""
    categories: Dict[str, List[CommandInfo]] = {}

    for cmd_info in COMMAND_INFO.values():
        if cmd_info.category not in categories:
            categories[cmd_info.category] = []
        categories[cmd_info.category].append(cmd_info)

    return categories


def get_all_commands() -> List[CommandInfo]:
    """Get all commands as a list."""
    return list(COMMAND_INFO.values())
