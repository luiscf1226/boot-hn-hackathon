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
    
    BINDINGS = [
        ("ctrl+c", "cleanup_and_quit", "Clean DB & Quit"),
        ("ctrl+l", "clear_terminal", "Clear Terminal"),
    ]
    
    def __init__(self):
        super().__init__()
        self._setup_step = None
        self._models = []
        self._current_command = None
        self._init_waiting_for_path = False
        self._clean_waiting_for_action = False
        self._pending_clean_action = None
        self._commit_waiting_for_confirmation = False
        self._pending_commit_message = None
        self._review_waiting_for_confirmation = False
        self._pending_review_data = None
        self._explain_waiting_for_input = False
        self._explain_input_type = None

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
                commands_text.append(" - Explain code from files or paste\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/commit", style="bold cyan")
                commands_text.append(" - AI-generated git commit messages\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/clean", style="bold cyan")
                commands_text.append(" - Database maintenance (clean/stats/vacuum)\n", style="white")
                commands_text.append("• ", style="dim")
                commands_text.append("/clear", style="bold cyan")
                commands_text.append(" - Clear terminal output\n", style="white")

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
        output = self.query_one("#output")
        output.write("Ready! Available commands: [bold]/setup[/bold], [bold]/models[/bold], [bold]/init[/bold], [bold]/clean[/bold], [bold]/commit[/bold], [bold]/explain[/bold], [bold]/clear[/bold]")
        output.write("[dim]💡 Tip: Use Ctrl+L to clear terminal, Ctrl+C to clean database and quit[/dim]")
        output.write("[dim]🖱️  You can select and copy text with your mouse![/dim]")
        self.query_one("#input").focus()
        
        # Hide progress bar initially
        progress = self.query_one("#progress")
        progress.display = False

    async def action_cleanup_and_quit(self) -> None:
        """Clean database and quit application."""
        output = self.query_one("#output")
        output.write("[blue]🧹 Cleaning database before exit...[/blue]")
        
        try:
            from app.functions.database_operations import clean_database
            result = clean_database()
            output.write(f"[green]{result}[/green]")
            await asyncio.sleep(1)  # Brief pause to show message
        except Exception as e:
            output.write(f"[red]❌ Error cleaning database: {e}[/red]")
            await asyncio.sleep(1)
        
        self.exit()

    async def action_clear_terminal(self) -> None:
        """Clear the terminal output."""
        output = self.query_one("#output")
        output.clear()
        output.write("🧹 Terminal cleared! Type [bold]/setup[/bold], [bold]/models[/bold], [bold]/init[/bold], [bold]/clean[/bold], [bold]/commit[/bold], [bold]/review-changes[/bold], [bold]/explain[/bold], or [bold]/clear[/bold].")

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
            
        # If we're waiting for clean action
        if self._clean_waiting_for_action:
            await self._handle_clean_action(output, text)
            return
            
        # If we're waiting for commit confirmation
        if self._commit_waiting_for_confirmation:
            await self._handle_commit_confirmation(output, text)
            return
            
        # If we're waiting for review confirmation
        if self._review_waiting_for_confirmation:
            await self._handle_review_confirmation(output, text)
            return
            
        # If we're waiting for explain input
        if self._explain_waiting_for_input:
            await self._handle_explain_input(output, text)
            return

        # Handle commands
        if text == "/setup":
            await self._handle_setup(output)
        elif text == "/models":
            await self._handle_models(output)
        elif text == "/init":
            await self._handle_init(output)
        elif text == "/clean":
            await self._handle_clean(output)
        elif text == "/commit":
            await self._handle_commit(output)
        elif text == "/review-changes":
            await self._handle_review(output)
        elif text == "/explain":
            await self._handle_explain(output)
        elif text == "/clear":
            await self.action_clear_terminal()
        elif text:
            output.write("[red]Unknown command. Use /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear[/red]")

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

    async def _handle_clean(self, output: RichLog) -> None:
        """Handle clean command step by step."""
        try:
            output.write("[blue]🧹 Database maintenance options...[/blue]")

            # Call clean command to get options
            result = await command_manager.execute_command("clean")

            if result.get("prompt") == "action":
                # Show available actions
                output.write(f"\n[green]{result['message']}[/green]")
                actions = result.get("actions", [])

                for i, action in enumerate(actions, 1):
                    output.write(f"  {i}. [bold]{action['key']}[/bold] - {action['desc']}")

                # Set state to wait for action selection
                output.write("[yellow]Enter action number or name (clean/stats/vacuum):[/yellow]")
                self._clean_waiting_for_action = True
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Enter action (1-3 or clean/stats/vacuum)"

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")

    async def _handle_clean_action(self, output: RichLog, choice: str) -> None:
        """Handle clean action selection."""
        try:
            # Allow empty input to cancel
            if not choice.strip():
                output.write("[dim]Clean operation cancelled.[/dim]")
                self._clean_waiting_for_action = False
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, or /clear"
                return

            # Map numbers to actions
            action_map = {"1": "clean", "2": "stats", "3": "vacuum"}
            action = action_map.get(choice, choice.lower())

            # Handle pending clean confirmation
            if hasattr(self, '_pending_clean_action') and self._pending_clean_action:
                if choice.lower() == "yes":
                    output.write("[blue]🧹 Cleaning database...[/blue]")
                    result = await command_manager.execute_command("clean", action=self._pending_clean_action)
                    if result.get("success"):
                        output.write(f"[green]{result['message']}[/green]")
                    else:
                        output.write(f"[red]{result['message']}[/red]")
                else:
                    output.write("[dim]Database clean cancelled.[/dim]")
                
                self._pending_clean_action = None
                self._clean_waiting_for_action = False
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, or /clear"
                return

            # Special warning for clean action
            if action == "clean":
                output.write("[red]⚠️  WARNING: This will permanently delete ALL data![/red]")
                output.write("[dim]Including: user settings, API keys, conversation history[/dim]")
                output.write("[yellow]Type 'yes' to confirm or anything else to cancel:[/yellow]")
                
                # Wait for confirmation
                self._pending_clean_action = action
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type 'yes' to confirm deletion"
                return

            # Execute non-destructive actions immediately
            result = await command_manager.execute_command("clean", action=action)

            if result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

            # Reset state
            self._clean_waiting_for_action = False
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, or /clear"

        except Exception as e:
            output.write(f"[red]Error during clean operation: {e}[/red]")
            self._clean_waiting_for_action = False
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"

    async def _handle_commit(self, output: RichLog) -> None:
        """Handle commit command step by step."""
        try:
            output.write("[blue]📝 Analyzing git repository and generating commit message...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar immediately
            self._show_progress("🤖 Initializing AI Commit Message Generator...")
            await asyncio.sleep(0.1)  # Small delay to ensure UI updates
            
            # Show progress animation for AI processing
            progress_task = asyncio.create_task(
                self._animate_progress(output, "🤖 AI Commit Message Generator", 45.0)
            )
            
            # Execute commit command
            command_task = asyncio.create_task(
                command_manager.execute_command("commit")
            )
            
            # Wait for command to complete
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()

            if result.get("prompt") == "commit_confirm":
                # Show staged files
                output.write(f"\n{result.get('staged_files', '')}")
                
                # Show AI-generated commit message
                commit_message = result.get("commit_message", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f'[yellow]"{commit_message}"[/yellow]')
                
                # Show AI info
                output.write(f"[dim]Generated by: {result.get('ai_model', 'Unknown')} (Session: {result.get('session_id', 'Unknown')})[/dim]")
                
                # Ask for confirmation
                output.write("\n[yellow]Execute this commit? (yes/no/edit):[/yellow]")
                output.write("[dim]• yes - Execute the commit[/dim]")
                output.write("[dim]• no - Cancel the commit[/dim]")
                output.write("[dim]• edit - Modify the message[/dim]")
                
                self._commit_waiting_for_confirmation = True
                self._pending_commit_message = commit_message
                input_widget = self.query_one("#input")
                input_widget.placeholder = "yes/no/edit"

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            # Ensure progress bar is hidden on error
            self._hide_progress()
            output.write(f"[red]❌ Error during commit: {e}[/red]")

    async def _handle_commit_confirmation(self, output: RichLog, choice: str) -> None:
        """Handle commit confirmation choice."""
        try:
            choice = choice.lower().strip()
            
            # Allow empty input to cancel
            if not choice or choice == "no":
                output.write("[dim]Commit cancelled.[/dim]")
                self._commit_waiting_for_confirmation = False
                self._pending_commit_message = None
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"
                return

            if choice == "yes":
                # Execute the commit
                output.write("[blue]🚀 Executing commit...[/blue]")
                result = await command_manager.execute_command("commit", action="execute", commit_message=self._pending_commit_message)

                if result.get("success"):
                    output.write(f"[green]{result['message']}[/green]")
                else:
                    output.write(f"[red]{result['message']}[/red]")

                # Reset state
                self._commit_waiting_for_confirmation = False
                self._pending_commit_message = None
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"

            elif choice == "edit":
                # Allow user to edit the commit message
                output.write(f"[yellow]Current message: \"{self._pending_commit_message}\"[/yellow]")
                output.write("[yellow]Enter your modified commit message:[/yellow]")
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Enter your commit message"
                # Stay in the same state, next input will be the new message

            elif choice.startswith("edit ") or (choice != "yes" and choice != "no" and self._pending_commit_message):
                # User provided a new commit message
                if choice.startswith("edit "):
                    new_message = choice[5:].strip()
                else:
                    new_message = choice
                
                if new_message:
                    self._pending_commit_message = new_message
                    output.write(f"[green]✅ Updated commit message: \"{new_message}\"[/green]")
                    output.write("[yellow]Execute this commit? (yes/no/edit):[/yellow]")
                    input_widget = self.query_one("#input")
                    input_widget.placeholder = "yes/no/edit"
                else:
                    output.write("[red]Empty commit message. Please try again.[/red]")

            else:
                output.write("[red]Please enter 'yes', 'no', or 'edit'[/red]")

        except Exception as e:
            output.write(f"[red]Error during commit confirmation: {e}[/red]")
            self._commit_waiting_for_confirmation = False
            self._pending_commit_message = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"

    async def _handle_review(self, output: RichLog) -> None:
        """Handle review-changes command."""
        try:
            from app.commands.command_manager import command_manager
            
            output.write("[blue]🔍 Running AI code review...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar immediately
            self._show_progress("🤖 Initializing AI Code Review...")
            await asyncio.sleep(0.1)  # Small delay to ensure UI updates
            
            # Show realistic progress with multiple steps
            progress_task = asyncio.create_task(self._animate_progress(output, "Review", 45.0))
            
            # Execute review command
            command_task = asyncio.create_task(
                command_manager.execute_command("review-changes")
            )
            
            # Wait for command to complete
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()

            if result.get("prompt") == "review_save_confirm":
                # Show git status
                output.write(f"\n{result.get('git_status', '')}")
                
                # Show AI review
                review_content = result.get("review_content", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{review_content}")
                
                # Show AI info
                output.write(f"[dim]Generated by: {result.get('ai_model', 'Unknown')} (Session: {result.get('session_id', 'Unknown')})[/dim]")
                
                # Ask for confirmation
                output.write("\n[yellow]Save this review to database? (yes/no):[/yellow]")
                output.write("[dim]• yes - Save review for future reference[/dim]")
                output.write("[dim]• no - Discard review[/dim]")
                
                self._review_waiting_for_confirmation = True
                self._pending_review_data = result
                input_widget = self.query_one("#input")
                input_widget.placeholder = "yes/no"

            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")

        except Exception as e:
            # Ensure progress bar is hidden on error
            self._hide_progress()
            output.write(f"[red]❌ Error during review: {e}[/red]")

    async def _handle_review_confirmation(self, output: RichLog, choice: str) -> None:
        """Handle review confirmation choice."""
        try:
            choice = choice.lower().strip()
            
            # Allow empty input to cancel
            if not choice or choice == "no":
                output.write("[dim]Review discarded (not saved to database).[/dim]")
                self._review_waiting_for_confirmation = False
                self._pending_review_data = None
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"
                return

            if choice == "yes":
                # Review is already saved to database via the agent.send_system_message call
                output.write("[green]✅ Code review saved to database successfully![/green]")
                session_id = self._pending_review_data.get("session_id", "Unknown")
                output.write(f"[dim]Session ID: {session_id}[/dim]")
                
                # Reset state
                self._review_waiting_for_confirmation = False
                self._pending_review_data = None
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"

            else:
                output.write("[red]Please enter 'yes' or 'no'[/red]")

        except Exception as e:
            output.write(f"[red]Error during review confirmation: {e}[/red]")
            self._review_waiting_for_confirmation = False
            self._pending_review_data = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"

    async def _handle_explain(self, output: RichLog) -> None:
        """Handle explain command."""
        try:
            output.write("[blue]🤖 Starting AI Code Explanation...[/blue]")
            
            # Get explanation options
            result = await command_manager.execute_command("explain")
            
            if result.get("prompt") == "explain_input":
                # Show available options
                output.write(f"\n[green]{result['message']}[/green]")
                options = result.get("data", {}).get("options", [])
                
                for i, option in enumerate(options, 1):
                    output.write(f"  {i}. [bold]{option['key']}[/bold] - {option['desc']}")
                
                # Set state to wait for option selection
                output.write("\n[yellow]Choose an option (1-3) or type your choice:[/yellow]")
                output.write("[dim]• paste - Paste code to analyze[/dim]")
                output.write("[dim]• file <path> - Analyze specific file[/dim]")
                output.write("[dim]• current - Analyze current directory[/dim]")
                
                self._explain_waiting_for_input = True
                self._explain_input_type = "option"
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Enter 1-3, paste, file <path>, or current"
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
        except Exception as e:
            output.write(f"[red]❌ Error starting explain: {e}[/red]")

    async def _handle_explain_input(self, output: RichLog, text: str) -> None:
        """Handle explain input."""
        try:
            # Allow empty input to cancel
            if not text.strip():
                output.write("[dim]Explain operation cancelled.[/dim]")
                self._explain_waiting_for_input = False
                self._explain_input_type = None
                input_widget = self.query_one("#input")
                input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"
                return

            text = text.strip()
            
            if self._explain_input_type == "option":
                # Handle option selection
                if text in ["1", "paste"]:
                    output.write("[blue]📝 Paste your code below and press Enter:[/blue]")
                    output.write("[dim]Tip: You can paste multi-line code. Press Enter when done.[/dim]")
                    self._explain_input_type = "code_paste"
                    input_widget = self.query_one("#input")
                    input_widget.placeholder = "Paste your code here..."
                    
                elif text in ["2", "file"] or text.startswith("file "):
                    if text.startswith("file "):
                        file_path = text[5:].strip()
                        await self._execute_explain_file(output, file_path)
                    else:
                        output.write("[blue]📁 Enter the file path to analyze:[/blue]")
                        output.write("[dim]Example: ./main.py or /path/to/file.py[/dim]")
                        self._explain_input_type = "file_path"
                        input_widget = self.query_one("#input")
                        input_widget.placeholder = "Enter file path..."
                        
                elif text in ["3", "current"]:
                    await self._execute_explain_current(output)
                    
                else:
                    output.write("[red]Invalid option. Please enter 1-3, paste, file, or current[/red]")
                    
            elif self._explain_input_type == "code_paste":
                # Handle pasted code
                await self._execute_explain_code(output, text)
                
            elif self._explain_input_type == "file_path":
                # Handle file path
                await self._execute_explain_file(output, text)
                
        except Exception as e:
            output.write(f"[red]❌ Error processing explain input: {e}[/red]")
            self._explain_waiting_for_input = False
            self._explain_input_type = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"

    async def _execute_explain_code(self, output: RichLog, code: str) -> None:
        """Execute code explanation."""
        try:
            output.write("[blue]🤖 Analyzing your code...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar
            self._show_progress("🤖 AI Code Analyzer")
            await asyncio.sleep(0.1)
            
            # Show progress animation
            progress_task = asyncio.create_task(
                self._animate_progress(output, "Code Analysis", 45.0)
            )
            
            # Execute command
            command_task = asyncio.create_task(
                command_manager.execute_command("explain", action="analyze_code", code=code)
            )
            
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()
            
            if result.get("success"):
                explanation = result.get("explanation_content", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{explanation}")
                output.write(f"\n[dim]AI Model: {result.get('ai_model', 'Unknown')} | Session: {result.get('session_id', 'Unknown')}[/dim]")
            else:
                error_msg = result.get("message", "Unknown error")
                output.write(f"[red]❌ Code analysis failed: {error_msg}[/red]")
                if "API key" in error_msg:
                    output.write("[dim]💡 Tip: Run /setup to configure your AI model[/dim]")
                    
        except Exception as e:
            output.write(f"[red]❌ Error analyzing code: {e}[/red]")
        finally:
            self._explain_waiting_for_input = False
            self._explain_input_type = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"

    async def _execute_explain_file(self, output: RichLog, file_path: str) -> None:
        """Execute file explanation."""
        try:
            output.write(f"[blue]🤖 Analyzing file: {file_path}[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar
            self._show_progress("🤖 AI File Analyzer")
            await asyncio.sleep(0.1)
            
            # Show progress animation
            progress_task = asyncio.create_task(
                self._animate_progress(output, "File Analysis", 45.0)
            )
            
            # Execute command
            command_task = asyncio.create_task(
                command_manager.execute_command("explain", action="analyze_file", file_path=file_path)
            )
            
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()
            
            if result.get("success"):
                explanation = result.get("explanation_content", "")
                file_name = result.get("file_name", file_path)
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{explanation}")
                output.write(f"\n[dim]File: {file_name} | Size: {result.get('file_size', 0)} chars | AI Model: {result.get('ai_model', 'Unknown')}[/dim]")
            else:
                error_msg = result.get("message", "Unknown error")
                output.write(f"[red]❌ File analysis failed: {error_msg}[/red]")
                if "API key" in error_msg:
                    output.write("[dim]💡 Tip: Run /setup to configure your AI model[/dim]")
                elif "not found" in error_msg.lower():
                    output.write("[dim]💡 Tip: Use absolute or relative paths like ./file.py or /full/path/file.py[/dim]")
                    
        except Exception as e:
            output.write(f"[red]❌ Error analyzing file: {e}[/red]")
        finally:
            self._explain_waiting_for_input = False
            self._explain_input_type = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"

    async def _execute_explain_current(self, output: RichLog) -> None:
        """Execute current directory explanation."""
        try:
            output.write("[blue]🤖 Analyzing current directory structure...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")
            
            # Show progress bar
            self._show_progress("🤖 AI Directory Analyzer")
            await asyncio.sleep(0.1)
            
            # Show progress animation
            progress_task = asyncio.create_task(
                self._animate_progress(output, "Directory Analysis", 45.0)
            )
            
            # Execute command
            command_task = asyncio.create_task(
                command_manager.execute_command("explain", action="analyze_current_dir")
            )
            
            try:
                result = await command_task
                progress_task.cancel()
                
                # Complete progress bar
                progress = self.query_one("#progress")
                progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self._hide_progress()
            
            if result.get("success"):
                explanation = result.get("explanation_content", "")
                directory_path = result.get("directory_path", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{explanation}")
                output.write(f"\n[dim]Directory: {directory_path} | AI Model: {result.get('ai_model', 'Unknown')}[/dim]")
            else:
                error_msg = result.get("message", "Unknown error")
                output.write(f"[red]❌ Directory analysis failed: {error_msg}[/red]")
                if "API key" in error_msg:
                    output.write("[dim]💡 Tip: Run /setup to configure your AI model[/dim]")
                    
        except Exception as e:
            output.write(f"[red]❌ Error analyzing directory: {e}[/red]")
        finally:
            self._explain_waiting_for_input = False
            self._explain_input_type = None
            input_widget = self.query_one("#input")
            input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"

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
        # Different loading messages based on the operation
        if "Commit" in message:
            loading_messages = [
                "🔍 Checking git repository status...",
                "📋 Analyzing staged files...",
                "📊 Reading git diff changes...",
                "🤖 Sending changes to AI for analysis...",
                "✍️  AI is crafting commit message...",
                "📝 Following git best practices...",
                "🎨 Formatting commit message...",
                "💾 Preparing commit preview..."
            ]
        elif "Review" in message:
            loading_messages = [
                "🔍 Checking git repository status...",
                "📊 Scanning code changes (staged & unstaged)...",
                "📁 Reading modified files...",
                "🔐 Analyzing security implications...",
                "🤖 Senior engineer AI reviewing code...",
                "⚠️  Identifying potential issues...",
                "💡 Generating improvement suggestions...",
                "🧪 Evaluating test coverage needs...",
                "📝 Preparing comprehensive review..."
            ]
        elif "Code Analysis" in message:
            loading_messages = [
                "🔍 Parsing code structure...",
                "📊 Analyzing syntax and patterns...",
                "🏗️  Identifying functions and classes...",
                "💡 Understanding code logic...",
                "🤖 AI expert analyzing implementation...",
                "📝 Breaking down algorithms...",
                "🎯 Identifying learning opportunities...",
                "⚠️  Checking for best practices...",
                "📚 Preparing educational explanation..."
            ]
        elif "File Analysis" in message:
            loading_messages = [
                "📁 Reading file contents...",
                "🔍 Analyzing file structure...",
                "📊 Identifying programming language...",
                "🏗️  Understanding architecture...",
                "🤖 AI expert reviewing code...",
                "💡 Extracting key concepts...",
                "🎯 Finding learning insights...",
                "📝 Analyzing code quality...",
                "📚 Preparing comprehensive explanation..."
            ]
        elif "Directory Analysis" in message:
            loading_messages = [
                "📁 Scanning directory structure...",
                "🔍 Identifying project files...",
                "📊 Analyzing project architecture...",
                "🏗️  Understanding file organization...",
                "🤖 AI architect reviewing structure...",
                "💡 Identifying technology stack...",
                "🎯 Finding architectural patterns...",
                "📝 Analyzing project conventions...",
                "📚 Preparing project insights..."
            ]
        else:
            # Default messages for init/documentation
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
        self._clean_waiting_for_action = False
        self._pending_clean_action = None
        self._commit_waiting_for_confirmation = False
        self._pending_commit_message = None
        self._review_waiting_for_confirmation = False
        self._pending_review_data = None
        input_widget = self.query_one("#input")
        input_widget.placeholder = "Type /setup, /models, /init, /clean, /commit, /review-changes, or /clear"


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
