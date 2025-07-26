"""
Welcome screen for the Textual UI.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog, ProgressBar
from rich.panel import Panel
from rich.text import Text
import asyncio

from app.commands.command_manager import command_manager



class WelcomeApp(App):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        self._setup_step = None
        self._models = []
        self._current_command = None
        self._init_waiting_for_path = False

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
                yield RichLog(
                    id="output", 
                    auto_scroll=True, 
                    max_lines=100,
                    highlight=True,
                    markup=True
                )
                
                # Progress bar (initially hidden)
                yield ProgressBar(id="progress", show_eta=False, show_percentage=False)
                
                # Command input
                yield Input(placeholder="Type /setup and press Enter", id="input")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app mounts."""
        output = self.query_one("#output")
        output.write("Ready! Type [bold]/setup[/bold] to configure your model.")
        self.query_one("#input").focus()
        
        # Hide progress bar initially
        progress = self.query_one("#progress")
        progress.display = False

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        output = self.query_one("#output")
        text = event.input.value.strip()

        # Clear input immediately
        event.input.value = ""

        output.write(f"[yellow]> {text}[/yellow]")

        # If we're in setup mode waiting for model selection
        if self._setup_step == "model_selection":
            await self._handle_model_choice(output, text)
            return
            
        # If we're waiting for init project path
        if self._init_waiting_for_path:
            await self._handle_init_path(output, text)
            return

        # Handle commands
        if text == "/setup":
            await self._handle_setup(output)
        elif text == "/models":
            await self._handle_models(output)
        elif text == "/init":
            await self._handle_init(output)
        elif text:
            output.write("[red]Unknown command. Use /setup, /models, or /init[/red]")

    async def _handle_setup(self, output: RichLog) -> None:
        """Handle setup command step by step."""
        try:
            output.write("[blue]Starting setup...[/blue]")

            # Call setup command
            result = await command_manager.execute_command("setup")

            if result.get("prompt") == "model":
                # Show models
                output.write(f"\n[green]{result['message']}[/green]")
                self._models = result.get("available_models", [])

                for i, model in enumerate(self._models, 1):
                    output.write(f"  {i}. {model}")

                # Set state to wait for model selection
                output.write("[yellow]Enter number (1-4):[/yellow]")
                self._setup_step = "model_selection"
                self._current_command = "setup"
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Enter number (1-4)"

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")

    async def _handle_models(self, output: RichLog) -> None:
        """Handle models command step by step."""
        try:
            output.write("[blue]Loading models...[/blue]")

            # Call models command
            result = await command_manager.execute_command("models")

            if result.get("prompt") == "model":
                # Show current model and available models
                output.write(f"\n[green]{result['message']}[/green]")
                self._models = result.get("available_models", [])
                current_model = result.get("current_model", "")

                for i, model in enumerate(self._models, 1):
                    current_indicator = " [dim](current)[/dim]" if model == current_model else ""
                    output.write(f"  {i}. {model}{current_indicator}")

                # Set state to wait for model selection
                output.write("[yellow]Enter number to change model (or press Enter to cancel):[/yellow]")
                self._setup_step = "model_selection"
                self._current_command = "models"
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Enter number (1-4) or press Enter"

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")

    async def _handle_init(self, output: RichLog) -> None:
        """Handle init command step by step."""
        try:
            output.write("[blue]Starting project initialization...[/blue]")

            # Call init command to check if we need project path
            result = await command_manager.execute_command("init")

            if result.get("prompt") == "project_path":
                # Ask for project path
                output.write(f"\n[green]{result['message']}[/green]")
                output.write("[yellow]Enter project path (or '.' for current directory):[/yellow]")
                self._init_waiting_for_path = True
                input_widget = self.query_one("#input")
                input_widget.placeholder = result.get("placeholder", "Enter project path")

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")

    def _show_progress(self, message: str = "Processing..."):
        """Show progress bar with message."""
        progress = self.query_one("#progress")
        progress.display = True
        progress.update(total=100)
        progress.advance(0)
        
        # Update progress bar label
        progress.label = message

    def _hide_progress(self):
        """Hide progress bar."""
        progress = self.query_one("#progress")
        progress.display = False

    async def _animate_progress(self, output: RichLog, message: str, duration: float = 60.0):
        """Animate progress bar and show loading messages."""
        # Loading messages to cycle through
        loading_messages = [
            "🔍 Analyzing project structure...",
            "📊 Identifying programming languages...",
            "📁 Reading important files...",
            "🤖 Sending to AI for analysis...",
            "✍️  AI is writing documentation...",
            "📝 Generating README.md...",
            "🎨 Formatting documentation...",
            "💾 Saving files..."
        ]
        
        progress = self.query_one("#progress")
        message_index = 0
        elapsed = 0.0
        step = 0.5  # Update every 0.5 seconds
        
        # Show first loading message immediately
        output.write(f"[dim]{loading_messages[0]}[/dim]")
        
        try:
            while elapsed < duration:
                # Update progress (simulate progress)
                progress_value = min(95, (elapsed / duration) * 100)
                progress.update(progress=progress_value)
                
                # Cycle through loading messages
                if elapsed > 0 and elapsed % 6 == 0:  # Change message every 6 seconds
                    message_index = (message_index + 1) % len(loading_messages)
                    output.write(f"[dim]{loading_messages[message_index]}[/dim]")
                
                await asyncio.sleep(step)
                elapsed += step
                
            progress.update(progress=100)
        except asyncio.CancelledError:
            # Progress animation was cancelled (command completed)
            pass

    async def _handle_init_path(self, output: RichLog, path: str) -> None:
        """Handle project path input for init command."""
        try:
            # Show immediate feedback and progress bar
            output.write("[blue]🚀 Starting AI-powered documentation generation...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar immediately
            self._show_progress("🤖 Initializing AI Documentation Generator...")
            await asyncio.sleep(0.1)  # Small delay to ensure UI updates
            
            # Start progress animation
            progress_task = asyncio.create_task(
                self._animate_progress(output, "🤖 AI Documentation Generator", 60.0)
            )
            
            # Give a moment for the UI to update before starting heavy work
            await asyncio.sleep(0.5)
            
            # Execute init command
            command_task = asyncio.create_task(
                command_manager.execute_command("init", project_path=path)
            )
            
            # Wait for command to complete, cancel progress if it finishes early
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                output.write("[dim]🎉 AI processing completed![/dim]")
                await asyncio.sleep(0.5)  # Brief pause to show completion
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()

            if result.get("success"):
                output.write(f"[green]✅ {result['message']}[/green]")
            else:
                error_msg = result.get('message', 'Unknown error')
                output.write(f"[red]❌ {error_msg}[/red]")
                
                # Show more helpful error details if available
                if "Details:" in error_msg:
                    output.write("[dim]💡 Troubleshooting tips:")
                    output.write("  • Set GEMINI_API_KEY in your .env file")
                    output.write("  • Run /setup to configure your model")
                    output.write("  • Check internet connection for AI service[/dim]")

            # Reset state
            self._init_waiting_for_path = False
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, or /init and press Enter"

        except Exception as e:
            # Ensure progress bar is hidden on error
            self._hide_progress()
            
            output.write(f"[red]❌ Error during initialization: {e}[/red]")
            output.write("[dim]💡 Try running /setup first to configure your API key[/dim]")
            self._init_waiting_for_path = False
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, or /init and press Enter"

    async def _handle_model_choice(self, output: RichLog, choice: str) -> None:
        """Handle model selection choice."""
        try:
            # Allow empty input to cancel
            if not choice.strip():
                output.write("[dim]Model selection cancelled.[/dim]")
                self._reset_state()
                return
                
            num = int(choice)
            if 1 <= num <= len(self._models):
                selected = self._models[num - 1]
                
                # Execute with selected model based on current command
                command = self._current_command or "setup"
                final_result = await command_manager.execute_command(command, model=selected)

                if final_result.get("success"):
                    output.write(f"[green]{final_result['message']}[/green]")
                else:
                    output.write(f"[red]{final_result['message']}[/red]")
                    
                # Reset state
                self._reset_state()
            else:
                output.write("[red]Invalid number. Please enter 1-4[/red]")
        except ValueError:
            output.write("[red]Please enter a number (1-4) or press Enter to cancel[/red]")

    def _reset_state(self):
        """Reset UI state after command completion."""
        self._setup_step = None
        self._models = []
        self._current_command = None
        self._init_waiting_for_path = False
        input_widget = self.query_one("#input")
        input_widget.placeholder = "Type /setup, /models, or /init and press Enter"


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
