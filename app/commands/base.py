"""
Base command classes and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session


class BaseCommand(ABC):
    """Base class for all agent commands."""

    def __init__(self, db_session: Session):
        self.db = db_session

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the command and return result."""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Get help text for the command."""
        pass


class CommandResult:
    """Standard result format for commands."""

    def __init__(
        self, success: bool, message: str, data: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.message = message
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {"success": self.success, "message": self.message, "data": self.data}
