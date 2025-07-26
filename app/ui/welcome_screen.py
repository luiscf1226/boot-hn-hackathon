"""
Welcome screen for the AI Coding Agent.
Displays welcome message and available commands.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, DataTable, Rule
from textual.binding import Binding
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Group
from rich.align import Align

from app.commands.command_enum import get_commands_by_category, CommandInfo


class WelcomeScreen(Static):
    """Welcome screen widget that displays agent information and commands."""

    def compose(self) -> ComposeResult:
        """Compose the welcome screen layout."""

        # Welcome message
        welcome_text = Text.from_markup(
            "[bold cyan]🤖 Welcome to boot-hn[/bold cyan]\n"
            "[bold white]The CLI Agent Buddy[/bold white]\n\n"
            "[dim]Your intelligent coding companion for development tasks[/dim]"
        )

        yield Static(
            Panel(
                Align.center(welcome_text),
                title="[bold green]AI Coding Agent[/bold green]",
                border_style="cyan",
                padding=(1, 2),
            ),
            id="welcome-header"
        )

        # Commands section
        yield Static(
            self._create_commands_display(),
            id="commands-section"
        )

        # Instructions
        instructions_text = Text.from_markup(
            "[bold yellow]Quick Start:[/bold yellow]\n"
            "• Press [bold cyan]Enter[/bold cyan] to start the command interface\n"
            "• Type [bold cyan]/setup[/bold cyan] to configure your agent\n"
            "• Type [bold cyan]/help[/bold cyan] for detailed help\n"
            "• Press [bold cyan]q[/bold cyan] or [bold cyan]Ctrl+C[/bold cyan] to quit"
        )

        yield Static(
            Panel(
                instructions_text,
                title="[bold blue]Instructions[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            ),
            id="instructions"
        )

    def _create_commands_display(self) -> Panel:
        """Create a formatted display of all available commands."""
        commands_by_category = get_commands_by_category()

        content_parts = []

        for category, commands in commands_by_category.items():
            # Category header
            category_text = Text(f"\n{category}", style="bold magenta")
            content_parts.append(category_text)
            content_parts.append(Text("─" * len(category), style="magenta"))

            # Commands in this category
            for cmd_info in commands:
                command_line = Text()
                command_line.append(f"  /{cmd_info.command.value}", style="bold cyan")
                command_line.append(" - ", style="dim")
                command_line.append(cmd_info.description, style="white")
                content_parts.append(command_line)

        # Combine all parts
        commands_text = Text("\n").join(content_parts)

        return Panel(
            commands_text,
            title="[bold green]Available Commands[/bold green]",
            border_style="green",
            padding=(1, 2),
        )


class WelcomeApp(App):
    """Main application class for the welcome screen."""

    CSS = """
    Screen {
        background: #0d1117;
    }

    #welcome-header {
        height: 8;
        margin: 1 2;
    }

    #commands-section {
        height: auto;
        margin: 0 2;
        overflow-y: scroll;
    }

    #instructions {
        height: 8;
        margin: 1 2;
    }

    Footer {
        background: #21262d;
    }

    Header {
        background: #161b22;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("enter", "start_command_interface", "Start Command Interface"),
        Binding("h", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(show_clock=True)

        with Container():
            yield WelcomeScreen()

        yield Footer()

    def action_quit(self) -> None:
        """Handle quit action."""
        self.exit()

    def action_start_command_interface(self) -> None:
        """Handle start command interface action."""
        from app.ui.command_screen import CommandScreen
        self.push_screen(CommandScreen())

    def action_show_help(self) -> None:
        """Handle show help action."""
        # Start command interface and show help
        from app.ui.command_screen import CommandScreen
        self.push_screen(CommandScreen())


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
