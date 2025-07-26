"""
Progress management utilities for the Textual UI.
"""

import asyncio
from textual.widgets import ProgressBar, RichLog


class ProgressManager:
    """Manages progress bar animations and loading messages."""

    def __init__(self, progress_widget: ProgressBar):
        self.progress = progress_widget

    def show(self, message: str = "Processing..."):
        """Show progress bar with message."""
        self.progress.display = True
        self.progress.update(total=100)
        self.progress.advance(0)
        self.progress.label = message

    def hide(self):
        """Hide progress bar."""
        self.progress.display = False

    async def animate(self, output: RichLog, message: str, duration: float = 60.0):
        """Animate progress bar and show loading messages."""
        loading_messages = self._get_loading_messages(message)
        elapsed = 0.0
        step = 0.5
        message_index = 0

        output.write(f"[dim]{loading_messages[0]}[/dim]")

        try:
            while elapsed < duration:
                progress_value = min(95, (elapsed / duration) * 100)
                self.progress.update(progress=progress_value)

                if elapsed > 0 and elapsed % 6 == 0:
                    message_index = (message_index + 1) % len(loading_messages)
                    output.write(f"[dim]{loading_messages[message_index]}[/dim]")

                await asyncio.sleep(step)
                elapsed += step

            self.progress.update(progress=100)
        except asyncio.CancelledError:
            pass

    def _get_loading_messages(self, message: str) -> list[str]:
        """Get appropriate loading messages based on operation type."""
        if "Commit" in message:
            return [
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
            return [
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
            return [
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
            return [
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
            return [
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
            return [
                "🔍 Analyzing project structure...",
                "📊 Identifying programming languages...",
                "📁 Reading important files...",
                "🤖 Sending to AI for analysis...",
                "✍️  AI is writing documentation...",
                "📝 Generating README.md...",
                "🎨 Formatting documentation...",
                "💾 Saving files..."
            ]