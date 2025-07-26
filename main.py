#!/usr/bin/env python3
"""
Main entry point for the AI Coding Agent.
Starts the Textual UI welcome screen.
"""

import sys
from pathlib import Path

def main():
    """Main entry point for the application."""
    try:
        print("🚀 Starting AI Coding Agent...")

        # Load environment variables
        print("📝 Loading environment...")

        # Add the project root to the Python path
        print("📁 Setting up paths...")
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        print("📦 Importing UI...")
        from app.ui.welcome_screen import WelcomeApp

        print("✅ Starting UI...")
        app = WelcomeApp()
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Goodbye! See you next time!")
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
