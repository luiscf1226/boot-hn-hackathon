"""
Utility functions and helpers.
"""

import os
import re
from typing import Optional, Dict


def create_env_file_if_not_exists():
    """Create .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Environment variables\n")
            f.write("# Add your configuration here\n\n")


def read_env_file() -> Dict[str, str]:
    """Read all environment variables from .env file."""
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env_variable(key: str, value: str) -> bool:
    """
    Save or update an environment variable in the .env file.

    Args:
        key: Environment variable name
        value: Environment variable value

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        create_env_file_if_not_exists()

        # Read existing content
        env_content = []
        key_found = False

        if os.path.exists(".env"):
            with open(".env", "r") as f:
                env_content = f.readlines()

        # Update or add the key
        for i, line in enumerate(env_content):
            if line.strip().startswith(f"{key}="):
                env_content[i] = f"{key}={value}\n"
                key_found = True
                break

        # If key not found, add it
        if not key_found:
            # Add section header if this is the first Gemini-related variable
            if key == "GEMINI_API_KEY":
                env_content.append("\n# Gemini AI Configuration\n")
            env_content.append(f"{key}={value}\n")

        # Write back to file
        with open(".env", "w") as f:
            f.writelines(env_content)

        # Update the current environment
        os.environ[key] = value

        return True

    except Exception as e:
        print(f"Error saving environment variable: {e}")
        return False


def get_env_variable(key: str, default: str = "") -> str:
    """
    Get environment variable value, checking both os.environ and .env file.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        str: Environment variable value or default
    """
    # First check current environment
    value = os.environ.get(key)
    if value:
        return value

    # Then check .env file
    env_vars = read_env_file()
    return env_vars.get(key, default)


def validate_gemini_api_key(api_key: str) -> bool:
    """
    Validate Gemini API key format.

    Args:
        api_key: API key to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    if not api_key or len(api_key.strip()) < 20:
        return False

    # Basic format validation for Gemini API keys
    # They typically start with "AIza" and are around 39 characters
    api_key = api_key.strip()
    if api_key.startswith("AIza") and len(api_key) >= 35:
        return True

    return False
