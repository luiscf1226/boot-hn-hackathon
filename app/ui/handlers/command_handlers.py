"""
Command handlers for the Textual UI.
"""

import asyncio
from textual.widgets import RichLog, Input
from app.commands.command_manager import command_manager
from app.ui.components.progress_manager import ProgressManager


class CommandHandlers:
    """Handles all command execution logic."""

    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager

    async def handle_setup(self, output: RichLog) -> dict:
        """Handle setup command step by step."""
        try:
            output.write("[blue]Starting setup...[/blue]")
            result = await command_manager.execute_command("setup")
            
            if result.get("prompt") == "api_key":
                output.write(f"\n[green]{result['message']}[/green]")
                instructions = result.get("instructions", [])
                for instruction in instructions:
                    output.write(f"[dim]• {instruction}[/dim]")
                output.write("\n[yellow]Enter your Gemini API key:[/yellow]")
                
            elif result.get("prompt") == "model":
                output.write(f"\n[green]{result['message']}[/green]")
                models = result.get("available_models", [])
                for i, model in enumerate(models, 1):
                    output.write(f"  {i}. {model}")
                output.write("[yellow]Enter number (1-4):[/yellow]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_models(self, output: RichLog) -> dict:
        """Handle models command step by step."""
        try:
            output.write("[blue]Loading models...[/blue]")
            result = await command_manager.execute_command("models")
            
            if result.get("prompt") == "model":
                output.write(f"\n[green]{result['message']}[/green]")
                models = result.get("available_models", [])
                current_model = result.get("current_model", "")
                
                for i, model in enumerate(models, 1):
                    current_indicator = " [dim](current)[/dim]" if model == current_model else ""
                    output.write(f"  {i}. {model}{current_indicator}")
                
                output.write("[yellow]Enter number to change model (or press Enter to cancel):[/yellow]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_init(self, output: RichLog) -> dict:
        """Handle init command step by step."""
        try:
            output.write("[blue]Starting project initialization...[/blue]")
            result = await command_manager.execute_command("init")
            
            if result.get("prompt") == "project_path":
                output.write(f"\n[green]{result['message']}[/green]")
                output.write("[yellow]Enter project path (or '.' for current directory):[/yellow]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_clean(self, output: RichLog) -> dict:
        """Handle clean command step by step."""
        try:
            output.write("[blue]🧹 Database maintenance options...[/blue]")
            result = await command_manager.execute_command("clean")
            
            if result.get("prompt") == "action":
                output.write(f"\n[green]{result['message']}[/green]")
                actions = result.get("actions", [])
                
                for i, action in enumerate(actions, 1):
                    output.write(f"  {i}. [bold]{action['key']}[/bold] - {action['desc']}")
                
                output.write("[yellow]Enter action number or name (clean/stats/vacuum):[/yellow]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            output.write(f"[red]Error: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_commit(self, output: RichLog) -> dict:
        """Handle commit command with progress animation."""
        try:
            output.write("[blue]📝 Analyzing git repository and generating commit message...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")

            self.progress_manager.show("🤖 Initializing AI Commit Message Generator...")
            await asyncio.sleep(0.1)

            progress_task = asyncio.create_task(
                self.progress_manager.animate(output, "🤖 AI Commit Message Generator", 45.0)
            )

            command_task = asyncio.create_task(
                command_manager.execute_command("commit")
            )

            try:
                result = await command_task
                progress_task.cancel()
                self.progress_manager.progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self.progress_manager.hide()

            if result.get("prompt") == "commit_confirm":
                output.write(f"\n{result.get('staged_files', '')}")
                commit_message = result.get("commit_message", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f'[yellow]"{commit_message}"[/yellow]')
                output.write(f"[dim]Generated by: {result.get('ai_model', 'Unknown')} (Session: {result.get('session_id', 'Unknown')})[/dim]")
                
                output.write("\n[yellow]Execute this commit? (yes/no/edit):[/yellow]")
                output.write("[dim]• yes - Execute the commit[/dim]")
                output.write("[dim]• no - Cancel the commit[/dim]")
                output.write("[dim]• edit - Modify the message[/dim]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            self.progress_manager.hide()
            output.write(f"[red]❌ Error during commit: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_review(self, output: RichLog) -> dict:
        """Handle review-changes command with progress animation."""
        try:
            output.write("[blue]🔍 Running AI code review...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")

            self.progress_manager.show("🤖 Initializing AI Code Review...")
            await asyncio.sleep(0.1)

            progress_task = asyncio.create_task(
                self.progress_manager.animate(output, "Review", 45.0)
            )

            command_task = asyncio.create_task(
                command_manager.execute_command("review-changes")
            )

            try:
                result = await command_task
                progress_task.cancel()
                self.progress_manager.progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self.progress_manager.hide()

            if result.get("prompt") == "review_save_confirm":
                output.write(f"\n{result.get('git_status', '')}")
                review_content = result.get("review_content", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{review_content}")
                output.write(f"[dim]Generated by: {result.get('ai_model', 'Unknown')} (Session: {result.get('session_id', 'Unknown')})[/dim]")
                
                output.write("\n[yellow]Save this review to database? (yes/no):[/yellow]")
                output.write("[dim]• yes - Save review for future reference[/dim]")
                output.write("[dim]• no - Discard review[/dim]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            self.progress_manager.hide()
            output.write(f"[red]❌ Error during review: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def handle_explain(self, output: RichLog) -> dict:
        """Handle explain command."""
        try:
            output.write("[blue]🤖 Starting AI Code Explanation...[/blue]")
            result = await command_manager.execute_command("explain")
            
            if result.get("prompt") == "explain_input":
                output.write(f"\n[green]{result['message']}[/green]")
                options = result.get("data", {}).get("options", [])
                
                for i, option in enumerate(options, 1):
                    output.write(f"  {i}. [bold]{option['key']}[/bold] - {option['desc']}")
                
                output.write("\n[yellow]Choose an option (1-3) or type your choice:[/yellow]")
                output.write("[dim]• paste - Paste code to analyze[/dim]")
                output.write("[dim]• file <path> - Analyze specific file[/dim]")
                output.write("[dim]• current - Analyze current directory[/dim]")
                
            elif result.get("success"):
                output.write(f"[green]{result['message']}[/green]")
            else:
                output.write(f"[red]{result['message']}[/red]")
                
            return result
        except Exception as e:
            output.write(f"[red]❌ Error starting explain: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def execute_explain_with_progress(self, output: RichLog, action: str, **kwargs) -> dict:
        """Execute explain command with progress animation."""
        try:
            analysis_type = {
                "analyze_code": "Code Analysis",
                "analyze_file": "File Analysis", 
                "analyze_current_dir": "Directory Analysis"
            }.get(action, "Analysis")
            
            output.write(f"[blue]🤖 Analyzing...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")

            self.progress_manager.show(f"🤖 AI {analysis_type}")
            await asyncio.sleep(0.1)

            progress_task = asyncio.create_task(
                self.progress_manager.animate(output, analysis_type, 45.0)
            )

            command_task = asyncio.create_task(
                command_manager.execute_command("explain", action=action, **kwargs)
            )

            try:
                result = await command_task
                progress_task.cancel()
                self.progress_manager.progress.update(progress=100)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self.progress_manager.hide()

            if result.get("success"):
                explanation = result.get("explanation_content", "")
                output.write(f"\n[green]{result['message']}[/green]")
                output.write(f"\n{explanation}")
                
                if action == "analyze_file":
                    file_name = result.get("file_name", kwargs.get("file_path", ""))
                    output.write(f"\n[dim]File: {file_name} | Size: {result.get('file_size', 0)} chars | AI Model: {result.get('ai_model', 'Unknown')}[/dim]")
                elif action == "analyze_current_dir":
                    directory_path = result.get("directory_path", "")
                    output.write(f"\n[dim]Directory: {directory_path} | AI Model: {result.get('ai_model', 'Unknown')}[/dim]")
                else:
                    output.write(f"\n[dim]AI Model: {result.get('ai_model', 'Unknown')} | Session: {result.get('session_id', 'Unknown')}[/dim]")
            else:
                error_msg = result.get("message", "Unknown error")
                output.write(f"[red]❌ Analysis failed: {error_msg}[/red]")
                if "API key" in error_msg:
                    output.write("[dim]💡 Tip: Run /setup to configure your AI model[/dim]")
                elif "not found" in error_msg.lower():
                    output.write("[dim]💡 Tip: Use absolute or relative paths like ./file.py or /full/path/file.py[/dim]")
                    
            return result
        except Exception as e:
            self.progress_manager.hide()
            output.write(f"[red]❌ Error during analysis: {e}[/red]")
            return {"success": False, "message": str(e)}

    async def execute_init_with_progress(self, output: RichLog, project_path: str) -> dict:
        """Execute init command with progress animation."""
        try:
            output.write("[blue]🚀 Starting AI-powered documentation generation...[/blue]")
            output.write("[yellow]⏳ Don't worry, it's not broken! We're calling the AI - this can take 30-60 seconds...[/yellow]")

            self.progress_manager.show("🤖 Initializing AI Documentation Generator...")
            await asyncio.sleep(0.1)

            progress_task = asyncio.create_task(
                self.progress_manager.animate(output, "🤖 AI Documentation Generator", 60.0)
            )

            await asyncio.sleep(0.5)

            command_task = asyncio.create_task(
                command_manager.execute_command("init", project_path=project_path)
            )

            try:
                result = await command_task
                progress_task.cancel()
                self.progress_manager.progress.update(progress=100)
                output.write("[dim]🎉 AI processing completed![/dim]")
                await asyncio.sleep(0.5)
                
            except Exception as e:
                progress_task.cancel()
                raise e
            finally:
                self.progress_manager.hide()

            if result.get("success"):
                output.write(f"[green]✅ {result['message']}[/green]")
            else:
                error_msg = result.get('message', 'Unknown error')
                output.write(f"[red]❌ {error_msg}[/red]")
                
                if "Details:" in error_msg:
                    output.write("[dim]💡 Troubleshooting tips:")
                    output.write("  • Set GEMINI_API_KEY in your .env file")
                    output.write("  • Run /setup to configure your model")
                    output.write("  • Check internet connection for AI service[/dim]")
                    
            return result
        except Exception as e:
            self.progress_manager.hide()
            output.write(f"[red]❌ Error during initialization: {e}[/red]")
            output.write("[dim]💡 Try running /setup first to configure your API key[/dim]")
            return {"success": False, "message": str(e)}