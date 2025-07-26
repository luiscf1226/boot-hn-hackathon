"""
Prompt loading utilities for commands.
"""

import os
from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{prompt_name}.txt"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()


def format_prompt(prompt_name: str, **kwargs) -> str:
    """Load and format a prompt template with variables."""
    template = load_prompt(prompt_name)
    return template.format(**kwargs)