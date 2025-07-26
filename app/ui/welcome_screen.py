"""
Welcome screen for the Textual UI.
"""

import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog
from rich.panel import Panel
from rich.text import Text

from app.commands.command_manager import command_manager



class WelcomeApp(App):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        self._waiting_for_input = False
        self._input_future: Optional[asyncio.Future] = None

    def compose(self) -> ComposeResult:
        """Compose the main app layout."""
        yield Header(show_clock=True)

        with Container():
            with Vertical():
                # Welcome message
                welcome_text = Text()
                welcome_text.append("🤖 Welcome to ", style="bold blue")
                welcome_text.append("Boot-hn", style="bold cyan")
                welcome_text.append("\nThe CLI Agent Buddy", style="dim")

                yield Static(Panel(
                    welcome_text,
                    title="[bold green]AI Coding Agent[/bold green]",
                    border_style="green"
                ))

                # Commands info
                commands_text = Text()
                commands_text.append("📋 Available Commands:\n\n", style="bold yellow")
                commands_text.append("• ", style="dim")
                commands_text.append("/setup", style="bold cyan")
                commands_text.append(" - Configure AI model\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/models", style="bold cyan")
                commands_text.append(" - Display models (coming soon)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/init", style="bold cyan")
                commands_text.append(" - Initialize project (coming soon)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/review-changes", style="bold cyan")
                commands_text.append(" - Review git changes (coming soon)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/explain", style="bold cyan")
                commands_text.append(" - Explain code (coming soon)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/commit", style="bold cyan")
                commands_text.append(" - Generate commit message (coming soon)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/clean", style="bold cyan")
                commands_text.append(" - Clean database (coming soon)\n", style="white")

                yield Static(Panel(
                    commands_text,
                    title="[bold blue]Commands[/bold blue]",
                    border_style="blue"
                ))

                # Command output log
                yield RichLog(id="output", auto_scroll=True, max_lines=100)
                
                # Command input
                yield Input(placeholder="Type /setup and press Enter", id="input")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app mounts."""
        output = self.query_one("#output")
        output.write("Ready! Type [bold]/setup[/bold] to configure your model.")
        self.query_one("#input").focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        output = self.query_one("#output")
        text = event.input.value.strip()

        # Clear input immediately
        event.input.value = ""

        output.write(f"[yellow]> {text}[/yellow]")

        # If we're waiting for user response to a prompt
        if self._waiting_for_input and self._input_future:
            self._input_future.set_result(text)
            return

        # Handle commands
        if text == "/setup":
            await self._handle_setup(output)
        elif text:
            output.write("[red]Unknown command. Use /setup[/red]")

    async def _handle_setup(self, output: RichLog) -> None:
        """Handle setup command step by step."""
        try:
            output.write("[blue]Starting setup...[/blue]")

            # Call setup command
            result = await command_manager.execute_command("setup")

            if result.get("prompt") == "model":
                # Show models
                output.write(f"\n[green]{result['message']}[/green]")
                models = result.get("available_models", [])

                for i, model in enumerate(models, 1):
                    output.write(f"  {i}. {model}")

                # Ask for input
                choice = await self._ask_user("Enter number (1-4):")

                # Parse choice
                try:
                    num = int(choice)
                    if 1 <= num <= len(models):
                        selected = models[num - 1]

                        # Execute with selected model
                        final_result = await command_manager.execute_command("setup", model=selected)

                        if final_result.get("success"):
                            output.write(f"[green]{final_result['message']}[/green]")
                        else:
                            output.write(f"[red]{final_result['message']}[/red]")
                    else:
                        output.write("[red]Invalid number[/red]")
                except ValueError:
                    output.write("[red]Please enter a number[/red]")

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")

    async def _ask_user(self, prompt: str) -> str:
        """Ask user for input and wait for response."""
        output = self.query_one("#output")
        input_widget = self.query_one("#input")

        output.write(f"[yellow]{prompt}[/yellow]")
        input_widget.placeholder = prompt

        # Set up future and wait
        self._waiting_for_input = True
        self._input_future = asyncio.get_event_loop().create_future()

        try:
            result = await self._input_future
            return result
        finally:
            self._waiting_for_input = False
            self._input_future = None
            input_widget.placeholder = "Type /setup and press Enter"


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
