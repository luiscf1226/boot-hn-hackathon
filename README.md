# 🤖 boot-hn - AI Coding Agent

A powerful CLI-based AI coding agent built with Python, FastAPI, and Textual UI. Your intelligent coding companion for development tasks.

## ✨ Features

- **Interactive Textual UI** - Beautiful terminal-based interface with command execution
- **AI-Powered Code Assistant** - Local Gemini AI integration
- **Focused Development Commands** - Essential workflow commands for coding
- **SQLite Database** - Local data storage with SQLAlchemy ORM
- **Clean Architecture** - SOLID principles with proper separation of concerns

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Start the AI Coding Agent
python main.py
```

### 3. Use the Command Interface

1. **Welcome Screen** - Shows available commands and instructions
2. **Press Enter** - Enters the command interface
3. **Type `/setup`** - Configure your Gemini API key and model
4. **Use other commands** - Type `/help` to see all available commands

## 🎯 Available Commands

### **Command Interface Usage:**
All commands must start with `/` and are executed in the command interface:

1. **`/setup`** - Configure Gemini API key and model selection
   - Prompts for API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - Choose from available models (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
   - Saves configuration to local SQLite database

2. **`/models`** - Display database models and relationships *(Coming Soon)*
3. **`/init`** - Create project documentation and save context *(Coming Soon)*
4. **`/review-changes`** - Git diff analysis and code review *(Coming Soon)*
5. **`/explain`** - Explain code from files or pasted content *(Coming Soon)*
6. **`/commit`** - Generate intelligent commit messages *(Coming Soon)*
7. **`/clean`** - Delete SQLite database and cleanup *(Coming Soon)*

### **UI Commands:**
- **`/help`** - Show detailed help with all commands
- **`/exit`** or **`/quit`** - Exit the application
- **`/clear`** - Clear command history
- **`Escape`** - Go back to welcome screen
- **`Ctrl+L`** - Clear command history (keyboard shortcut)

## 🎮 How to Use

### **1. Start the Application**
```bash
python main.py
```

### **2. Welcome Screen**
- Shows all available commands
- Press `Enter` to start command interface
- Press `q` or `Ctrl+C` to quit

### **3. Command Interface**
- Type commands starting with `/`
- Example: `/setup` to configure agent
- Press `Escape` to go back to welcome
- View command history in the scrollable area

### **4. Setup Your Agent (First Time)**
```
$ /setup

🤖 Welcome to Agent Setup!
==================================================

🔑 Gemini API Key Configuration
-----------------------------------
Please enter your Gemini API key:
(You can get one from: https://makersuite.google.com/app/apikey)

🔑 API Key: [your_api_key_here]

🤖 Model Selection
--------------------
Available Gemini models:
  1. gemini-2.0-flash-exp
  2. gemini-1.5-pro
  3. gemini-1.5-flash
  4. gemini-pro

🤖 Model choice: 2
✅ Selected: gemini-1.5-pro

✅ Setup completed successfully!
🔑 API Key: ****your_key
🤖 Selected Model: gemini-1.5-pro
```

## 🏗️ Project Structure

```
hackathon/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── alembic.ini               # Alembic configuration
├── app/
│   ├── commands/             # Command implementations
│   │   ├── command_enum.py   # Available commands enum
│   │   ├── command_manager.py # Command execution manager
│   │   ├── setup_command.py  # Setup command (fully implemented)
│   │   └── base.py          # Base command classes
│   ├── models/              # SQLAlchemy models
│   │   └── user.py          # User & settings models with business logic
│   ├── core/                # Core utilities
│   │   ├── config.py        # Application configuration
│   │   └── database.py      # Database connection
│   └── ui/                  # Textual UI components
│       ├── welcome_screen.py # Welcome screen
│       └── command_screen.py # Command interface
```

## 🛠️ Architecture

This project follows **Clean Architecture** principles:

- **🎨 UI Layer** (`app/ui/`) - Textual interface components
- **⚡ Command Layer** (`app/commands/`) - Command execution and user interaction
- **💾 Model Layer** (`app/models/`) - Business logic and data operations
- **🔧 Core Layer** (`app/core/`) - Configuration and database infrastructure

### **Key Design Principles:**
- ✅ **Single Responsibility** - Each class has one clear purpose
- ✅ **Separation of Concerns** - UI, commands, and data logic are separate
- ✅ **Dependency Inversion** - Commands depend on model abstractions
- ✅ **Clean Interfaces** - Clear contracts between layers

## 🔧 Development Status

- ✅ **Setup Command** - Complete and functional
- ✅ **UI Integration** - Command interface working
- ✅ **Database Layer** - User and settings models
- ✅ **Command Architecture** - Extensible command system
- 🔄 **Other Commands** - Coming soon (models, init, review-changes, etc.)

## 📝 Next Steps

1. ✅ **Setup Command** - Complete with UI integration
2. 🔄 **Models Command** - Display database models and relationships
3. 🔄 **Init Command** - Create documentation and context
4. 🔄 **Review Changes** - Git diff analysis
5. 🔄 **Explain Command** - Code explanation
6. 🔄 **Commit Command** - Smart commit messages
7. 🔄 **Clean Command** - Database cleanup

## 📝 License

This project is part of a hackathon and is intended for educational and development purposes.

---

**Happy Coding! 🚀**

Ready to get started? Run `python main.py` and type `/setup` to configure your agent!
