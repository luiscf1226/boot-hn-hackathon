"""
Commands panel component for the Textual UI.
"""

from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text


class CommandsPanel:
    """Creates the commands panel for the main UI."""

    @staticmethod
    def create() -> Static:
        """Create the commands panel widget."""
        commands_text = Text()
        commands_text.append("📋 Available Commands:\n\n", style="bold yellow")
        
        commands = [
            ("/setup", "Configure AI model"),
            ("/models", "Display models (coming soon)"),
            ("/init", "Initialize project (coming soon)"),
            ("/review-changes", "Review git changes (coming soon)"),
            ("/explain", "Explain code from files or paste"),
            ("/commit", "AI-generated git commit messages"),
            ("/clean", "Database maintenance (clean/stats/vacuum)"),
            ("/clear", "Clear terminal output")
        ]
        
        for command, description in commands:
            commands_text.append("• ", style="dim")
            commands_text.append(command, style="bold cyan")
            commands_text.append(f" - {description}\n", style="white")

        return Static(Panel(
            commands_text,
            title="[bold blue]Commands[/bold blue]",
            border_style="blue"
        ))