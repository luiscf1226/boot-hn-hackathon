#!/usr/bin/env python3
"""
Simple test to check if Textual UI is working
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Container

class TestApp(App):
    """Simple test app to check if input works."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield RichLog(id="output")
            yield Input(placeholder="Type something and press Enter...", id="input")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app starts."""
        self.query_one("#input").focus()
        output = self.query_one("#output")
        output.write("Test app started. Type something and press Enter.")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        output = self.query_one("#output")
        text = event.input.value.strip()
        output.write(f"You typed: {text}")
        event.input.value = ""

        if text.lower() in ["quit", "exit"]:
            self.exit()

if __name__ == "__main__":
    app = TestApp()
    app.run()
