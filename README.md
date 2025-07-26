# AI Coding Agent

AI-powered coding assistant with terminal UI for code analysis, commit messages, and project management.

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
pip install git+https://github.com/luiscf1226/boot-hn-hackathon.git
ai-coding-agent
```

### Option 2: Install from Source

```bash
git clone https://github.com/luiscf1226/boot-hn-hackathon.git
cd boot-hn-hackathon
python3 -m venv venv
source venv/bin/activate  # Linux/macOS (Windows: venv\Scripts\activate)
pip install -e .
ai-coding-agent
```

## Usage

Run the application:
```bash
ai-coding-agent
# or short alias:
aca
```

### Available Commands
- `/setup` - Configure AI model and API key
- `/explain` - Explain code from files or paste
- `/commit` - Generate AI commit messages
- `/review` - Review code changes
- `/clean` - Clean database

## Configuration

On first run, the app will guide you through setup:
1. Enter your Google Gemini API key
2. Select an AI model
3. Start using the commands

## Uninstall

```bash
pip uninstall ai-coding-agent
```

## Requirements

- Python 3.8+
- Git
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)