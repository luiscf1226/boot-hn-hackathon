# AI Coding Agent

AI-powered coding assistant with terminal UI for code analysis, commit messages, and project management.

## About This Project

This is a hackathon project for boot.dev!

First of all I want to be honest ( Sorry Lane). I did use AI for the UI with claude and tab. I had no experience with textual and toml for creating projects, but the project idea, commands and functions were an idea from a boot.dev course so it was easy to guide from that and write the code for commands and functions and AI call

I learned a lot recently on how to use classes and use patterns like builder and factory I hope you notice!

I'm not sure if I'm gonna win but I'm just happy to represent Honduras and hope at least you found it interesting! 🇭🇳

## Get Your Free API Key

Before using this app, you'll need a **free** Google Gemini API key:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your key (keep it safe!)

**Free tier includes:** 15 requests per minute, 1 million tokens per minute, 1,500 requests per day - perfect for personal use!

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

### Running the Application
```bash
# After installation via pip:
ai-coding-agent
# or short alias:
aca
```

### Running Locally from Clone
```bash
# Clone and setup
git clone https://github.com/luiscf1226/boot-hn-hackathon.git
cd boot-hn-hackathon
python3 -m venv venv
source venv/bin/activate  # Linux/macOS (Windows: venv\Scripts\activate)
pip install -e .

# Run the application
ai-coding-agent
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

## Project Structure

```
app/
├── commands/           # Command implementations
│   ├── prompts/       # AI prompt templates
│   └── *.py          # Individual command files
├── core/              # Core functionality
├── models/            # Database models
├── ui/                # Textual UI components
└── cli.py            # Entry point
```

## Adding New Commands

To add a new command:

1. **Create command file** in `app/commands/`:
   ```python
   # app/commands/my_command.py
   from app.commands.base import BaseCommand
   
   class MyCommand(BaseCommand):
       async def execute(self, *args, **kwargs):
           return {"success": True, "message": "Command executed!"}
   ```

2. **Add to command enum** in `app/commands/command_enum.py`:
   ```python
   MY_COMMAND = "mycommand"
   ```

3. **Register in command manager** in `app/commands/command_manager.py`:
   ```python
   from app.commands.my_command import MyCommand
   self._commands[AgentCommand.MY_COMMAND] = MyCommand
   ```

4. **Add to UI** in `app/ui/components/commands_panel.py` for display

## Requirements

- Python 3.8+
- Git
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)
