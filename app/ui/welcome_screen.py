"""
Welcome screen for the Textual UI.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, RichLog, ProgressBar
import asyncio

from app.commands.command_manager import command_manager
from app.ui.components.welcome_panel import WelcomePanel
from app.ui.components.commands_panel import CommandsPanel
from app.ui.components.progress_manager import ProgressManager
from app.ui.handlers.command_handlers import CommandHandlers
from app.ui.state.app_state import AppState


class WelcomeApp(App):
    """Main application class."""

    BINDINGS = [
        ("ctrl+c", "cleanup_and_quit", "Clean DB & Quit"),
        ("ctrl+l", "clear_terminal", "Clear Terminal"),
    ]

    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.progress_manager = None
        self.command_handlers = None

    def compose(self) -> ComposeResult:
        """Compose the main app layout."""
        yield Header(show_clock=True)

        with Container():
            with Vertical():
                # Welcome message
                yield WelcomePanel.create()

                # Commands info
                yield CommandsPanel.create()

                # Command output log
                yield RichLog(
                    id="output",
                    auto_scroll=True,
                    max_lines=100,
                    highlight=True,
                    markup=True,
                    wrap=True
                )

                # Progress bar (initially hidden)
                yield ProgressBar(id="progress", show_eta=False, show_percentage=False)

                # Command input
                yield Input(placeholder="Type /setup and press Enter", id="input")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app mounts."""
        # Initialize managers
        progress_widget = self.query_one("#progress")
        self.progress_manager = ProgressManager(progress_widget)
        self.command_handlers = CommandHandlers(self.progress_manager)

        output = self.query_one("#output")
        output.write("Ready! Available commands: [bold]/setup[/bold], [bold]/models[/bold], [bold]/init[/bold], [bold]/clean[/bold], [bold]/commit[/bold], [bold]/explain[/bold], [bold]/clear[/bold]")
        output.write("[dim]Tip: Use Ctrl+L to clear terminal, Ctrl+C to clean database and quit[/dim]")
        output.write("[dim]You can select and copy text with your mouse![/dim]")
        self.query_one("#input").focus()

        # Hide progress bar initially
        progress_widget.display = False

    async def action_cleanup_and_quit(self) -> None:
        """Clean database and quit application."""
        output = self.query_one("#output")
        output.write("[blue]Cleaning database before exit...[/blue]")

        try:
            from app.functions.database_operations import clean_database
            result = clean_database()
            output.write(f"[green]{result}[/green]")
            await asyncio.sleep(1)  # Brief pause to show message
        except Exception as e:
            output.write(f"[red]Error cleaning database: {e}[/red]")
            await asyncio.sleep(1)

        self.exit()

    async def action_clear_terminal(self) -> None:
        """Clear the terminal output."""
        output = self.query_one("#output")
        output.clear()
        output.write("Terminal cleared! Type [bold]/setup[/bold], [bold]/models[/bold], [bold]/init[/bold], [bold]/clean[/bold], [bold]/commit[/bold], [bold]/review-changes[/bold], [bold]/explain[/bold], or [bold]/clear[/bold].")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        output = self.query_one("#output")
        text = event.input.value.strip()

        # Clear input immediately
        event.input.value = ""
        output.write(f"[yellow]> {text}[/yellow]")

        # Handle state-specific inputs
        if self.state.setup_waiting_for_api_key:
            await self._handle_api_key_input(output, text)
            return

        if self.state.setup_step == "model_selection":
            await self._handle_model_choice(output, text)
            return

        if self.state.init_waiting_for_path:
            await self._handle_init_path(output, text)
            return

        if self.state.clean_waiting_for_action:
            await self._handle_clean_action(output, text)
            return

        if self.state.commit_waiting_for_confirmation:
            await self._handle_commit_confirmation(output, text)
            return

        if self.state.review_waiting_for_confirmation:
            await self._handle_review_confirmation(output, text)
            return

        if self.state.explain_waiting_for_input:
            await self._handle_explain_input(output, text)
            return

        # Handle commands
        await self._handle_command(output, text)

    async def _handle_command(self, output: RichLog, text: str) -> None:
        """Handle main command routing."""
        input_widget = self.query_one("#input")

        if text == "/setup":
            result = await self.command_handlers.handle_setup(output)
            await self._process_setup_result(result, input_widget)
        elif text == "/models":
            result = await self.command_handlers.handle_models(output)
            await self._process_models_result(result, input_widget)
        elif text == "/init":
            result = await self.command_handlers.handle_init(output)
            await self._process_init_result(result, input_widget)
        elif text == "/clean":
            result = await self.command_handlers.handle_clean(output)
            await self._process_clean_result(result, input_widget)
        elif text == "/commit":
            result = await self.command_handlers.handle_commit(output)
            await self._process_commit_result(result, input_widget)
        elif text == "/review-changes":
            result = await self.command_handlers.handle_review(output)
            await self._process_review_result(result, input_widget)
        elif text == "/explain":
            result = await self.command_handlers.handle_explain(output)
            await self._process_explain_result(result, input_widget)
        elif text == "/clear":
            await self.action_clear_terminal()
        elif text:
            output.write("[red]Unknown command. Use /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear[/red]")

    async def _process_setup_result(self, result: dict, input_widget: Input) -> None:
        """Process setup command result and update state."""
        if result.get("prompt") == "api_key":
            self.state.setup_waiting_for_api_key = True
            input_widget.placeholder = result.get("placeholder", "Paste your Gemini API key here...")
        elif result.get("prompt") == "model":
            self.state.models = result.get("available_models", [])
            self.state.setup_step = "model_selection"
            self.state.current_command = "setup"
            input_widget.placeholder = "Enter number (1-4)"
        else:
            self._update_default_placeholder(input_widget)

    async def _process_models_result(self, result: dict, input_widget: Input) -> None:
        """Process models command result and update state."""
        if result.get("prompt") == "model":
            self.state.models = result.get("available_models", [])
            self.state.setup_step = "model_selection"
            self.state.current_command = "models"
            input_widget.placeholder = "Enter number (1-4) or press Enter"
        else:
            self._update_default_placeholder(input_widget)

    async def _process_init_result(self, result: dict, input_widget: Input) -> None:
        """Process init command result and update state."""
        if result.get("prompt") == "project_path":
            self.state.init_waiting_for_path = True
            input_widget.placeholder = result.get("placeholder", "Enter project path")
        else:
            self._update_default_placeholder(input_widget)

    async def _process_clean_result(self, result: dict, input_widget: Input) -> None:
        """Process clean command result and update state."""
        if result.get("prompt") == "action":
            self.state.clean_waiting_for_action = True
            input_widget.placeholder = "Enter action (1-3 or clean/stats/vacuum)"
        else:
            self._update_default_placeholder(input_widget)

    async def _process_commit_result(self, result: dict, input_widget: Input) -> None:
        """Process commit command result and update state."""
        if result.get("prompt") == "commit_confirm":
            self.state.commit_waiting_for_confirmation = True
            self.state.pending_commit_message = result.get("commit_message", "")
            input_widget.placeholder = "yes/no/edit"
        else:
            self._update_default_placeholder(input_widget)

    async def _process_review_result(self, result: dict, input_widget: Input) -> None:
        """Process review command result and update state."""
        if result.get("prompt") == "review_save_confirm":
            self.state.review_waiting_for_confirmation = True
            self.state.pending_review_data = result
            input_widget.placeholder = "yes/no"
        else:
            self._update_default_placeholder(input_widget)

    async def _process_explain_result(self, result: dict, input_widget: Input) -> None:
        """Process explain command result and update state."""
        if result.get("prompt") == "explain_input":
            self.state.explain_waiting_for_input = True
            self.state.explain_input_type = "option"
            input_widget.placeholder = "Enter 1-3, paste, file <path>, or current"
        else:
            self._update_default_placeholder(input_widget)

    def _update_default_placeholder(self, input_widget: Input) -> None:
        """Update input placeholder to default state."""
        input_widget.placeholder = self.state.get_placeholder_text()

    async def _handle_api_key_input(self, output: RichLog, api_key: str) -> None:
        """Handle API key input during setup."""
        input_widget = self.query_one("#input")

        try:
            if not api_key.strip():
                output.write("[dim]Setup cancelled.[/dim]")
                self.state.setup_waiting_for_api_key = False
                self._update_default_placeholder(input_widget)
                return

            result = await command_manager.execute_command("setup", api_key=api_key)

            if result.get("prompt") == "api_key":
                output.write(f"\n[red]{result['message']}[/red]")
                instructions = result.get("instructions", [])
                for instruction in instructions:
                    output.write(f"[dim]• {instruction}[/dim]")
                output.write("\n[yellow]Please enter a valid Gemini API key:[/yellow]")
                input_widget.placeholder = result.get("placeholder", "Paste your Gemini API key here...")

            elif result.get("success") and result.get("api_key_saved"):
                output.write(f"[green]{result['message']}[/green]")
                self.state.setup_waiting_for_api_key = False

                model_result = await command_manager.execute_command("setup")
                if model_result.get("prompt") == "model":
                    output.write(f"\n[green]{model_result['message']}[/green]")
                    self.state.models = model_result.get("available_models", [])

                    for i, model in enumerate(self.state.models, 1):
                        output.write(f"  {i}. {model}")

                    output.write("[yellow]Enter number (1-4):[/yellow]")
                    self.state.setup_step = "model_selection"
                    self.state.current_command = "setup"
                    input_widget.placeholder = "Enter number (1-4)"
                else:
                    output.write(f"[green]API key saved! Run /setup again to select model.[/green]")
                    self.state.reset()
                    self._update_default_placeholder(input_widget)

            else:
                output.write(f"[red]{result.get('message', 'Unknown error')}[/red]")
                self.state.setup_waiting_for_api_key = False
                self._update_default_placeholder(input_widget)

        except Exception as e:
            output.write(f"[red]Error processing API key: {e}[/red]")
            self.state.setup_waiting_for_api_key = False
            self._update_default_placeholder(input_widget)

    async def _handle_model_choice(self, output: RichLog, choice: str) -> None:
        """Handle model selection choice."""
        input_widget = self.query_one("#input")

        try:
            if not choice.strip():
                output.write("[dim]Model selection cancelled.[/dim]")
                self.state.reset()
                self._update_default_placeholder(input_widget)
                return

            num = int(choice)
            if 1 <= num <= len(self.state.models):
                selected = self.state.models[num - 1]

                command = self.state.current_command or "setup"
                final_result = await command_manager.execute_command(command, model=selected)

                if final_result.get("success"):
                    output.write(f"[green]{final_result['message']}[/green]")
                else:
                    output.write(f"[red]{final_result['message']}[/red]")

                self.state.reset()
                self._update_default_placeholder(input_widget)
            else:
                output.write("[red]Invalid number. Please enter 1-4[/red]")
        except ValueError:
            output.write("[red]Please enter a number (1-4) or press Enter to cancel[/red]")

    async def _handle_init_path(self, output: RichLog, path: str) -> None:
        """Handle project path input for init command."""
        input_widget = self.query_one("#input")

        try:
            result = await self.command_handlers.execute_init_with_progress(output, path)
            self.state.init_waiting_for_path = False
            self._update_default_placeholder(input_widget)
        except Exception as e:
            output.write(f"[red]Error during initialization: {e}[/red]")
            self.state.init_waiting_for_path = False
            self._update_default_placeholder(input_widget)

    async def _handle_clean_action(self, output: RichLog, choice: str) -> None:
        """Handle clean action selection."""
        input_widget = self.query_one("#input")

        try:
            if not choice.strip():
                output.write("[dim]Clean operation cancelled.[/dim]")
                self.state.clean_waiting_for_action = False
                self.state.pending_clean_action = None
                self._update_default_placeholder(input_widget)
                return

            action_map = {"1": "clean", "2": "stats", "3": "vacuum"}
            action = action_map.get(choice, choice.lower())

            if hasattr(self.state, 'pending_clean_action') and self.state.pending_clean_action:
                if choice.lower() == "yes":
                    output.write("[blue]Cleaning database...[/blue]")
                    result = await command_manager.execute_command("clean", action=self.state.pending_clean_action)
                    if result.get("success"):
                        output.write(f"[green]{result['message']}[/green]")
                    else:
                        output.write(f"[red]{result['message']}[/red]")
                else:
                    output.write("[dim]Database clean cancelled.[/dim]")

                self.state.pending_clean_action = None
                self.state.clean_waiting_for_action = False
                self._update_default_placeholder(input_widget)
                return

            if action == "clean":
                output.write("[red]WARNING: This will permanently delete ALL data![/red]")
                output.write("[dim]Including: user settings, API keys, conversation history[/dim]")
                output.write("[yellow]Type 'yes' to confirm or anything else to cancel:[/yellow]")

                self.state.pending_clean_action = action
                input_widget.placeholder = "Type 'yes' to confirm deletion"
                return

            result = await command_manager.execute_command("clean", action=action)

            if result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

            self.state.clean_waiting_for_action = False
            self._update_default_placeholder(input_widget)

        except Exception as e:
            output.write(f"[red]Error during clean operation: {e}[/red]")
            self.state.clean_waiting_for_action = False
            self._update_default_placeholder(input_widget)

    async def _handle_commit_confirmation(self, output: RichLog, choice: str) -> None:
        """Handle commit confirmation choice."""
        input_widget = self.query_one("#input")

        try:
            choice = choice.lower().strip()

            if not choice or choice == "no":
                output.write("[dim]Commit cancelled.[/dim]")
                self.state.commit_waiting_for_confirmation = False
                self.state.pending_commit_message = None
                self._update_default_placeholder(input_widget)
                return

            if choice == "yes":
                output.write("[blue]Executing commit...[/blue]")
                result = await command_manager.execute_command("commit", action="execute", commit_message=self.state.pending_commit_message)

                if result.get("success"):
                    output.write(f"[green]{result['message']}[/green]")
                else:
                    output.write(f"[red]{result['message']}[/red]")

                self.state.commit_waiting_for_confirmation = False
                self.state.pending_commit_message = None
                self._update_default_placeholder(input_widget)

            elif choice == "edit":
                output.write(f"[yellow]Current message: \"{self.state.pending_commit_message}\"[/yellow]")
                output.write("[yellow]Enter your modified commit message:[/yellow]")
                input_widget.placeholder = "Enter your commit message"

            elif choice.startswith("edit ") or (choice != "yes" and choice != "no" and self.state.pending_commit_message):
                if choice.startswith("edit "):
                    new_message = choice[5:].strip()
                else:
                    new_message = choice

                if new_message:
                    self.state.pending_commit_message = new_message
                    output.write(f"[green]Updated commit message: \"{new_message}\"[/green]")
                    output.write("[yellow]Execute this commit? (yes/no/edit):[/yellow]")
                    input_widget.placeholder = "yes/no/edit"
                else:
                    output.write("[red]Empty commit message. Please try again.[/red]")

            else:
                output.write("[red]Please enter 'yes', 'no', or 'edit'[/red]")

        except Exception as e:
            output.write(f"[red]Error during commit confirmation: {e}[/red]")
            self.state.commit_waiting_for_confirmation = False
            self.state.pending_commit_message = None
            self._update_default_placeholder(input_widget)

    async def _handle_review_confirmation(self, output: RichLog, choice: str) -> None:
        """Handle review confirmation choice."""
        input_widget = self.query_one("#input")

        try:
            choice = choice.lower().strip()

            if not choice or choice == "no":
                output.write("[dim]Review discarded (not saved to database)[/dim]")
                self.state.review_waiting_for_confirmation = False
                self.state.pending_review_data = None
                self._update_default_placeholder(input_widget)
                return

            if choice == "yes":
                output.write("[green]Code review saved to database successfully![/green]")
                session_id = self.state.pending_review_data.get("session_id", "Unknown")
                output.write(f"[dim]Session ID: {session_id}[/dim]")

                self.state.review_waiting_for_confirmation = False
                self.state.pending_review_data = None
                self._update_default_placeholder(input_widget)

            else:
                output.write("[red]Please enter 'yes' or 'no'[/red]")

        except Exception as e:
            output.write(f"[red]Error during review confirmation: {e}[/red]")
            self.state.review_waiting_for_confirmation = False
            self.state.pending_review_data = None
            self._update_default_placeholder(input_widget)

    async def _handle_explain_input(self, output: RichLog, text: str) -> None:
        """Handle explain input."""
        input_widget = self.query_one("#input")

        try:
            if not text.strip():
                output.write("[dim]Explain operation cancelled.[/dim]")
                self.state.explain_waiting_for_input = False
                self.state.explain_input_type = None
                self._update_default_placeholder(input_widget)
                return

            text = text.strip()

            if self.state.explain_input_type == "option":
                if text in ["1", "paste"]:
                    output.write("[blue]Paste your code below and press Enter:[/blue]")
                    output.write("[dim]Tip: You can paste multi-line code. Press Enter when done.[/dim]")
                    self.state.explain_input_type = "code_paste"
                    input_widget.placeholder = "Paste your code here..."

                elif text in ["2", "file"] or text.startswith("file "):
                    if text.startswith("file "):
                        file_path = text[5:].strip()
                        await self.command_handlers.execute_explain_with_progress(output, "analyze_file", file_path=file_path)
                        self.state.explain_waiting_for_input = False
                        self.state.explain_input_type = None
                        self._update_default_placeholder(input_widget)
                    else:
                        output.write("[blue]Enter the file path to analyze:[/blue]")
                        output.write("[dim]Example: ./main.py or /path/to/file.py[/dim]")
                        self.state.explain_input_type = "file_path"
                        input_widget.placeholder = "Enter file path..."

                elif text in ["3", "current"]:
                    await self.command_handlers.execute_explain_with_progress(output, "analyze_current_dir")
                    self.state.explain_waiting_for_input = False
                    self.state.explain_input_type = None
                    self._update_default_placeholder(input_widget)

                else:
                    output.write("[red]Invalid option. Please enter 1-3, paste, file, or current[/red]")

            elif self.state.explain_input_type == "code_paste":
                await self.command_handlers.execute_explain_with_progress(output, "analyze_code", code=text)
                self.state.explain_waiting_for_input = False
                self.state.explain_input_type = None
                self._update_default_placeholder(input_widget)

            elif self.state.explain_input_type == "file_path":
                await self.command_handlers.execute_explain_with_progress(output, "analyze_file", file_path=text)
                self.state.explain_waiting_for_input = False
                self.state.explain_input_type = None
                self._update_default_placeholder(input_widget)

        except Exception as e:
            output.write(f"[red]Error processing explain input: {e}[/red]")
            self.state.explain_waiting_for_input = False
            self.state.explain_input_type = None
            self._update_default_placeholder(input_widget)


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
