# 🤖 boot-hn - AI Coding Agent

A powerful CLI-based AI coding agent built with Python, FastAPI, and Textual UI. Your intelligent coding companion for development tasks.

## ✨ Features

- **Interactive Textual UI** - Beautiful terminal-based interface
- **AI-Powered Code Assistant** - Local Gemini AI integration
- **Comprehensive Commands** - File operations, code analysis, project management
- **FastAPI Backend** - RESTful API for agent operations
- **SQLite Database** - Local data storage with SQLAlchemy ORM
- **JWT Authentication** - Secure session management
- **Alembic Migrations** - Database schema management

## 🏗️ Project Structure

```
hackathon/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── alembic.ini               # Alembic configuration
├── alembic/                  # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/                      # Main application package
│   ├── __init__.py
│   ├── api/                  # FastAPI routes and dependencies
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── agent.py
│   │   │   └── commands.py
│   │   └── dependencies.py
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── command.py
│   │   └── session.py
│   ├── services/             # Business logic services
│   │   ├── agent_service.py
│   │   ├── auth_service.py
│   │   ├── command_service.py
│   │   └── ai_service.py
│   ├── functions/            # Agent functions
│   │   ├── code_analysis.py
│   │   ├── file_operations.py
│   │   └── code_generation.py
│   ├── commands/             # Command definitions
│   │   ├── command_enum.py   # Available commands enum
│   │   ├── base.py
│   │   ├── code_commands.py
│   │   └── file_commands.py
│   ├── agent/                # Agent core logic
│   │   ├── core.py
│   │   ├── context.py
│   │   └── memory.py
│   ├── ui/                   # Textual UI components
│   │   ├── welcome_screen.py # Welcome screen
│   │   ├── main_screen.py
│   │   ├── chat_screen.py
│   │   └── components/
│   ├── core/                 # Core utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   └── utils/                # Helper utilities
│       ├── logger.py
│       └── helpers.py
```

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

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configurations
# Update AI_API_URL, SECRET_KEY, etc.
```

### 3. Initialize Database

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Start the welcome screen
python main.py
```

## 🎮 Usage

### Welcome Screen
- Displays all available commands organized by category
- Press `Enter` to start the agent
- Press `h` for help
- Press `q` or `Ctrl+C` to quit

### Available Commands

#### File Operations
- `create_file` - Create a new file with specified content
- `read_file` - Read and display the contents of a file
- `edit_file` - Edit an existing file
- `delete_file` - Delete a file from the filesystem
- `list_files` - List files in a directory

#### Code Operations
- `analyze_code` - Analyze code for issues and improvements
- `generate_code` - Generate code based on requirements
- `refactor_code` - Refactor existing code for better structure
- `debug_code` - Help debug code issues
- `format_code` - Format code according to standards

#### Project Operations
- `create_project` - Create a new project structure
- `build_project` - Build the current project
- `test_project` - Run tests for the project
- `deploy_project` - Deploy the project

#### AI Operations
- `ask_ai` - Ask the AI agent a question
- `explain_code` - Get AI explanation of code
- `suggest_improvements` - Get AI suggestions for improvements
- `generate_docs` - Generate documentation using AI

#### System Operations
- `execute_command` - Execute a system command
- `install_package` - Install a package or dependency
- `search_files` - Search for files or content

#### Agent Operations
- `show_help` - Show help information
- `show_status` - Show agent status and context
- `clear_context` - Clear the agent's context
- `exit` - Exit the agent

## 🛠️ Development

This project follows clean architecture principles and is designed for extensibility. Each component is modular and can be developed independently.

### Key Technologies
- **Python 3.8+** - Programming language
- **FastAPI** - Web framework for APIs
- **Textual** - Terminal user interface framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation and settings
- **Rich** - Rich text and beautiful formatting

### Architecture Principles
- SOLID principles
- Clean Architecture
- Domain-Driven Design (DDD)
- CQRS pattern support
- Event-driven architecture ready

## 📝 License

This project is part of a hackathon and is intended for educational and development purposes.

---

**Happy Coding! 🚀**
# boot-hn-hackathon
