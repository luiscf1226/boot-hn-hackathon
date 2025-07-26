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

        # Add the package root to Python path if not already there
        current_dir = Path(__file__).parent.parent.absolute()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        # Import and run the main application
        from main import main as run_app

        run_app()

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
