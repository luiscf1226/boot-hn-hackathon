"""
Command manager for handling command execution.
"""

import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.commands.command_enum import AgentCommand
from app.commands.setup_command import SetupCommand
from app.core.database import get_db


class CommandManager:
    """Manages command execution and routing."""

    def __init__(self):
        self._commands = {}
        self._register_commands()

    def _register_commands(self):
        """Register all available commands."""
        # Register setup command
        self._commands[AgentCommand.SETUP] = SetupCommand

        # TODO: Register other commands as they are implemented
        # self._commands[AgentCommand.MODELS] = ModelsCommand
        # self._commands[AgentCommand.INIT] = InitCommand
        # etc.

    async def execute_command(self, command_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a command by name."""
        try:
            # Get command enum
            command_enum = None
            for cmd in AgentCommand:
                if cmd.value == command_name.lower().strip():
                    command_enum = cmd
                    break

            if not command_enum:
                return {
                    "success": False,
                    "message": f"Unknown command: {command_name}",
                    "data": {"available_commands": [cmd.value for cmd in AgentCommand]}
                }

            # Check if command is registered
            if command_enum not in self._commands:
                return {
                    "success": False,
                    "message": f"Command '{command_name}' is not implemented yet",
                    "data": {}
                }

            # Get database session
            db_gen = get_db()
            db = next(db_gen)

            try:
                # Create command instance
                command_class = self._commands[command_enum]
                command_instance = command_class(db)

                # Execute command
                result = await command_instance.execute(*args, **kwargs)
                return result

            finally:
                db.close()

        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing command: {str(e)}",
                "data": {}
            }

    def get_available_commands(self) -> list:
        """Get list of available command names."""
        return [cmd.value for cmd in self._commands.keys()]

    def is_command_available(self, command_name: str) -> bool:
        """Check if a command is available."""
        for cmd in AgentCommand:
            if cmd.value == command_name.lower().strip():
                return cmd in self._commands
        return False


# Global command manager instance
command_manager = CommandManager()
