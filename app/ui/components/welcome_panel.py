"""
Welcome panel component for the Textual UI.
"""

from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text


class WelcomePanel:
    """Creates the welcome panel for the main UI."""

    @staticmethod
    def create() -> Static:
        """Create the welcome panel widget."""
        welcome_text = Text()
        welcome_text.append("🤖 Welcome to ", style="bold blue")
        welcome_text.append("Boot-hn", style="bold cyan")
        welcome_text.append("\nThe CLI Agent Buddy", style="dim")

        return Static(Panel(
            welcome_text,
            title="[bold green]AI Coding Agent[/bold green]",
            border_style="green"
        ))