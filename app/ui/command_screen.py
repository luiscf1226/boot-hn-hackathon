"""
Command screen for the Textual UI.
"""

import asyncio
from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, RichLog, Static

from app.commands.command_manager import command_manager


class CommandScreen(Screen):
    """Screen for command input and execution."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+c", "app.quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._input_future: Optional[asyncio.Future] = None

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        with Container():
            yield Static("🤖 AI Coding Agent - Command Interface\nType commands starting with '/' (e.g., /setup)", id="info")
            yield RichLog(
                id="command-history",
                highlight=True,
                markup=True,
                auto_scroll=True,
                max_lines=1000
            )
            yield Input(
                placeholder="Enter a command (e.g., /setup)...",
                id="command-input"
            )
            yield Static("", id="status")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when screen mounts."""
        self.query_one("#command-input").focus()
        history = self.query_one("#command-history")
        history.write("Welcome! Type [bold]/setup[/bold] to configure your AI model.")

    async def _prompt_user(self, message: str) -> str:
        """Prompt user for input and wait for response."""
        history = self.query_one("#command-history")
        input_widget = self.query_one("#command-input")

        # Display the prompt
        history.write(f"\n[yellow]? {message}[/yellow]")

        # Set placeholder to show what we're asking for
        input_widget.placeholder = message
        input_widget.focus()

        # Create a future to wait for user input
        self._input_future = asyncio.get_event_loop().create_future()

        # Wait for user input with timeout
        try:
            result = await asyncio.wait_for(self._input_future, timeout=300.0)  # 5 minute timeout
            return result
        except asyncio.TimeoutError:
            history.write("[red]Input timeout. Please try again.[/red]")
            return ""
        except Exception as e:
            history.write(f"[red]Input error: {e}[/red]")
            return ""
        finally:
            if self._input_future and not self._input_future.done():
                self._input_future.cancel()
            self._input_future = None
            input_widget.placeholder = "Enter a command (e.g., /setup)..."

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input submission."""
        try:
            history = self.query_one("#command-history")
            command_input = event.input
            command_text = command_input.value.strip()

            # If we're waiting for a prompt response
            if self._input_future is not None and not self._input_future.done():
                try:
                    self._input_future.set_result(command_text)
                except Exception:
                    # Future might have been cancelled or already set
                    pass
                command_input.value = ""
                return

            if not command_text:
                return

            # Clear input
            command_input.value = ""
            history.write(f"\n[bold yellow]$ {command_text}[/bold yellow]")

            # Process command
            await self._process_command(command_text, history)

        except Exception as e:
            try:
                history = self.query_one("#command-history")
                history.write(f"[red]Error: {e}[/red]")
            except:
                pass

    async def _process_command(self, command_text: str, history: RichLog) -> None:
        """Process a command."""
        try:
            if not command_text.startswith("/"):
                history.write("[red]Commands must start with '/' (e.g., /setup)[/red]")
                return

            command_name = command_text[1:].strip()

            if command_name == "setup":
                await self._handle_setup_command(history)
            else:
                history.write(f"[red]Unknown command: {command_name}[/red]")
                history.write("Available commands: [bold]setup[/bold]")

        except Exception as e:
            history.write(f"[red]Error processing command: {e}[/red]")

    async def _handle_setup_command(self, history: RichLog) -> None:
        """Handle the setup command with simplified model selection."""
        try:
            # Start setup process
            result = await command_manager.execute_command("setup")

            if not result.get("success"):
                if "prompt" in result and result["prompt"] == "model":
                    # Show available models
                    history.write(f"\n[green]{result['message']}[/green]")
                    models = result.get("available_models", [])
                    for i, model in enumerate(models, 1):
                        current = " [dim](current)[/dim]" if model == result.get("current_model") else ""
                        history.write(f"  {i}. {model}{current}")

                    # Ask user to select model
                    model_choice = await self._prompt_user("Enter model number or name:")

                    # Parse user choice
                    selected_model = None
                    if model_choice.isdigit():
                        idx = int(model_choice) - 1
                        if 0 <= idx < len(models):
                            selected_model = models[idx]
                    else:
                        if model_choice in models:
                            selected_model = model_choice

                    if not selected_model:
                        history.write("[red]Invalid selection. Please try again.[/red]")
                        return

                    # Execute setup with selected model
                    final_result = await command_manager.execute_command("setup", model=selected_model)

                    if final_result.get("success"):
                        history.write(f"[green]{final_result['message']}[/green]")
                    else:
                        history.write(f"[red]{final_result['message']}[/red]")
                else:
                    history.write(f"[red]{result['message']}[/red]")
            else:
                history.write(f"[green]{result['message']}[/green]")

        except Exception as e:
            history.write(f"[red]Setup failed: {e}[/red]")
