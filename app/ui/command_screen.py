"""
Command screen for the AI Coding Agent.
Handles command input and execution within the UI.
"""

import asyncio
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.screen import Screen
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel

from app.commands.command_manager import command_manager
from app.commands.command_enum import get_all_commands


class CommandScreen(Screen):
    """Screen for command input and execution."""

    CSS = """
    CommandScreen {
        background: #0d1117;
    }

    #command-history {
        height: 1fr;
        margin: 1 2;
        border: solid #30363d;
        background: #161b22;
    }

    #command-input-container {
        height: 3;
        margin: 0 2 1 2;
    }

    #command-input {
        background: #21262d;
        color: #f0f6fc;
        border: solid #30363d;
    }

    #status-bar {
        height: 3;
        margin: 0 2;
        background: #161b22;
        border: solid #30363d;
    }

    Header {
        background: #161b22;
    }

    Footer {
        background: #21262d;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("escape", "back", "Back to Welcome"),
        Binding("ctrl+l", "clear", "Clear History"),
    ]

    def __init__(self):
        super().__init__()
        self.command_history = []

    def compose(self) -> ComposeResult:
        """Compose the command screen layout."""
        yield Header(show_clock=True)

        with Container():
            # Command history display
            yield RichLog(
                highlight=True,
                markup=True,
                id="command-history"
            )

            # Status bar
            yield Static(
                Panel(
                    Text("Ready for commands. Type /help for available commands, /setup to configure agent.",
                         style="dim"),
                    title="[bold blue]Status[/bold blue]",
                    border_style="blue"
                ),
                id="status-bar"
            )

            # Command input
            with Container(id="command-input-container"):
                yield Input(
                    placeholder="Type a command (e.g., /setup, /help)...",
                    id="command-input"
                )

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.query_one("#command-input").focus()

        # Welcome message
        history = self.query_one("#command-history")
        history.write(Panel(
            Text.from_markup(
                "[bold cyan]🤖 Boot-hn AI Coding Agent - Command Interface[/bold cyan]\n\n"
                "[white]Available commands:[/white]\n"
                "[cyan]• /setup[/cyan] - Configure Gemini API and model\n"
                "[cyan]• /models[/cyan] - Display database models\n"
                "[cyan]• /init[/cyan] - Initialize project documentation\n"
                "[cyan]• /review-changes[/cyan] - Review git changes\n"
                "[cyan]• /explain[/cyan] - Explain code\n"
                "[cyan]• /commit[/cyan] - Generate commit message\n"
                "[cyan]• /clean[/cyan] - Clean database\n"
                "[cyan]• /help[/cyan] - Show detailed help\n"
                "[cyan]• /exit[/cyan] - Exit agent\n\n"
                "[dim]Type a command and press Enter to execute[/dim]"
            ),
            title="[bold green]Welcome[/bold green]",
            border_style="green"
        ))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input submission."""
        command_input = event.input
        command_text = command_input.value.strip()

        if not command_text:
            return

        # Clear input
        command_input.value = ""

        # Add command to history display
        history = self.query_one("#command-history")
        history.write(f"\n[bold yellow]$ {command_text}[/bold yellow]")

        # Process command
        await self._process_command(command_text, history)

    async def _process_command(self, command_text: str, history: RichLog) -> None:
        """Process a command and display results."""
        # Handle built-in UI commands
        if command_text.lower() in ["/exit", "/quit"]:
            self.app.exit()
            return

        if command_text.lower() == "/help":
            self._show_help(history)
            return

        if command_text.lower() == "/clear":
            history.clear()
            return

        # Parse command (remove leading slash)
        if command_text.startswith("/"):
            command_name = command_text[1:].lower().strip()
        else:
            history.write("[red]❌ Commands must start with '/' (e.g., /setup)[/red]")
            return

        # Check if command is available
        if not command_manager.is_command_available(command_name):
            available_commands = command_manager.get_available_commands()
            history.write(f"[red]❌ Unknown command: {command_name}[/red]")
            history.write(f"[dim]Available: {', '.join(available_commands)}[/dim]")
            return

        # Update status
        self._update_status(f"Executing command: {command_name}")

        try:
            # Execute command
            history.write(f"[blue]🚀 Executing {command_name}...[/blue]")

            # For setup command, we need to handle it specially since it has interactive prompts
            if command_name == "setup":
                await self._handle_setup_command(history)
            else:
                # For other commands, execute normally
                result = await command_manager.execute_command(command_name)
                self._display_command_result(result, history)

        except Exception as e:
            history.write(f"[red]❌ Error executing command: {str(e)}[/red]")
        finally:
            self._update_status("Ready for commands")

    async def _handle_setup_command(self, history: RichLog) -> None:
        """Handle setup command with special UI consideration."""
        history.write("[yellow]⚠️  Setup command requires interactive input.[/yellow]")
        history.write("[cyan]🔄 Switching to setup mode...[/cyan]")

        # Execute setup command
        result = await command_manager.execute_command("setup")
        self._display_command_result(result, history)

    def _display_command_result(self, result: dict, history: RichLog) -> None:
        """Display command execution result."""
        if result.get("success"):
            history.write(f"[green]✅ {result.get('message', 'Command completed successfully')}[/green]")

            # Display additional data if available
            if result.get("data"):
                data = result["data"]
                if data.get("model"):
                    history.write(f"[cyan]🤖 Model: {data['model']}[/cyan]")
                if data.get("api_key_set"):
                    history.write("[cyan]🔑 API Key: Configured[/cyan]")
        else:
            history.write(f"[red]❌ {result.get('message', 'Command failed')}[/red]")

    def _show_help(self, history: RichLog) -> None:
        """Show help information."""
        commands = get_all_commands()

        help_text = Text()
        help_text.append("📚 Available Commands:\n\n", style="bold blue")

        current_category = None
        for cmd_info in commands:
            if cmd_info.category != current_category:
                current_category = cmd_info.category
                help_text.append(f"\n{current_category}:\n", style="bold magenta")

            help_text.append(f"  /{cmd_info.command.value}", style="bold cyan")
            help_text.append(f" - {cmd_info.description}\n", style="white")

        help_text.append("\n💡 Tips:\n", style="bold yellow")
        help_text.append("• Commands must start with '/'\n", style="dim")
        help_text.append("• Press Ctrl+L to clear history\n", style="dim")
        help_text.append("• Press Escape to go back to welcome screen\n", style="dim")

        history.write(Panel(
            help_text,
            title="[bold blue]Help[/bold blue]",
            border_style="blue"
        ))

    def _update_status(self, message: str) -> None:
        """Update the status bar."""
        status_widget = self.query_one("#status-bar")
        status_widget.update(Panel(
            Text(message, style="dim"),
            title="[bold blue]Status[/bold blue]",
            border_style="blue"
        ))

    def action_back(self) -> None:
        """Go back to welcome screen."""
        self.app.pop_screen()

    def action_clear(self) -> None:
        """Clear command history."""
        history = self.query_one("#command-history")
        history.clear()
        self._update_status("History cleared")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
