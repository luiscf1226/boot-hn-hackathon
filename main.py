#!/usr/bin/env python3
"""
Main entry point for the AI Coding Agent.
Starts the Textual UI welcome screen.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.ui.welcome_screen import WelcomeApp
from app.core.database import create_tables


def main():
    """Main entry point for the application."""
    try:
        # Initialize database
        print("🔧 Initializing database...")
        create_tables()
        print("✅ Database initialized")

        # Start the UI application
        print("🚀 Starting AI Coding Agent...")
        app = WelcomeApp()
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Goodbye! See you next time!")
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
