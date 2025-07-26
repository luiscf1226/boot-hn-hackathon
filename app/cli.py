#!/usr/bin/env python3
"""
Command-line interface entry point for AI Coding Agent.
This module provides the main entry point for the console script.
"""

import sys
import os
from pathlib import Path


def main():
    """Main entry point for the AI Coding Agent console script."""
    try:
        print("🚀 Starting AI Coding Agent...")
        print("Loading environment...")
        print("Setting up paths...")
        print("Importing UI...")
        
        # Import and run the application directly
        from app.ui.welcome_screen import WelcomeApp

        print("Starting UI...")
        app = WelcomeApp()
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Goodbye! See you next time!")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install ai-coding-agent")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        import traceback

        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
