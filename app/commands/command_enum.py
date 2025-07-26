"""
Command enumeration for the AI Coding Agent.
Defines all available commands that the agent can execute.
"""

from enum import Enum
from typing import Dict, List


class AgentCommand(Enum):
    """Enumeration of all available agent commands."""

    # File operations
    CREATE_FILE = "create_file"
    READ_FILE = "read_file"
    EDIT_FILE = "edit_file"
    DELETE_FILE = "delete_file"
    LIST_FILES = "list_files"

    # Code operations
    ANALYZE_CODE = "analyze_code"
    GENERATE_CODE = "generate_code"
    REFACTOR_CODE = "refactor_code"
    DEBUG_CODE = "debug_code"
    FORMAT_CODE = "format_code"

    # Project operations
    CREATE_PROJECT = "create_project"
    BUILD_PROJECT = "build_project"
    TEST_PROJECT = "test_project"
    DEPLOY_PROJECT = "deploy_project"

    # AI operations
    ASK_AI = "ask_ai"
    EXPLAIN_CODE = "explain_code"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    GENERATE_DOCS = "generate_docs"

    # System operations
    EXECUTE_COMMAND = "execute_command"
    INSTALL_PACKAGE = "install_package"
    SEARCH_FILES = "search_files"

    # Agent operations
    SHOW_HELP = "show_help"
    SHOW_STATUS = "show_status"
    CLEAR_CONTEXT = "clear_context"
    EXIT = "exit"


class CommandInfo:
    """Information about a command."""

    def __init__(self, command: AgentCommand, description: str, category: str):
        self.command = command
        self.description = description
        self.category = category


# Command descriptions and categories
COMMAND_INFO: Dict[AgentCommand, CommandInfo] = {
    # File operations
    AgentCommand.CREATE_FILE: CommandInfo(
        AgentCommand.CREATE_FILE,
        "Create a new file with specified content",
        "File Operations"
    ),
    AgentCommand.READ_FILE: CommandInfo(
        AgentCommand.READ_FILE,
        "Read and display the contents of a file",
        "File Operations"
    ),
    AgentCommand.EDIT_FILE: CommandInfo(
        AgentCommand.EDIT_FILE,
        "Edit an existing file",
        "File Operations"
    ),
    AgentCommand.DELETE_FILE: CommandInfo(
        AgentCommand.DELETE_FILE,
        "Delete a file from the filesystem",
        "File Operations"
    ),
    AgentCommand.LIST_FILES: CommandInfo(
        AgentCommand.LIST_FILES,
        "List files in a directory",
        "File Operations"
    ),

    # Code operations
    AgentCommand.ANALYZE_CODE: CommandInfo(
        AgentCommand.ANALYZE_CODE,
        "Analyze code for issues and improvements",
        "Code Operations"
    ),
    AgentCommand.GENERATE_CODE: CommandInfo(
        AgentCommand.GENERATE_CODE,
        "Generate code based on requirements",
        "Code Operations"
    ),
    AgentCommand.REFACTOR_CODE: CommandInfo(
        AgentCommand.REFACTOR_CODE,
        "Refactor existing code for better structure",
        "Code Operations"
    ),
    AgentCommand.DEBUG_CODE: CommandInfo(
        AgentCommand.DEBUG_CODE,
        "Help debug code issues",
        "Code Operations"
    ),
    AgentCommand.FORMAT_CODE: CommandInfo(
        AgentCommand.FORMAT_CODE,
        "Format code according to standards",
        "Code Operations"
    ),

    # Project operations
    AgentCommand.CREATE_PROJECT: CommandInfo(
        AgentCommand.CREATE_PROJECT,
        "Create a new project structure",
        "Project Operations"
    ),
    AgentCommand.BUILD_PROJECT: CommandInfo(
        AgentCommand.BUILD_PROJECT,
        "Build the current project",
        "Project Operations"
    ),
    AgentCommand.TEST_PROJECT: CommandInfo(
        AgentCommand.TEST_PROJECT,
        "Run tests for the project",
        "Project Operations"
    ),
    AgentCommand.DEPLOY_PROJECT: CommandInfo(
        AgentCommand.DEPLOY_PROJECT,
        "Deploy the project",
        "Project Operations"
    ),

    # AI operations
    AgentCommand.ASK_AI: CommandInfo(
        AgentCommand.ASK_AI,
        "Ask the AI agent a question",
        "AI Operations"
    ),
    AgentCommand.EXPLAIN_CODE: CommandInfo(
        AgentCommand.EXPLAIN_CODE,
        "Get AI explanation of code",
        "AI Operations"
    ),
    AgentCommand.SUGGEST_IMPROVEMENTS: CommandInfo(
        AgentCommand.SUGGEST_IMPROVEMENTS,
        "Get AI suggestions for improvements",
        "AI Operations"
    ),
    AgentCommand.GENERATE_DOCS: CommandInfo(
        AgentCommand.GENERATE_DOCS,
        "Generate documentation using AI",
        "AI Operations"
    ),

    # System operations
    AgentCommand.EXECUTE_COMMAND: CommandInfo(
        AgentCommand.EXECUTE_COMMAND,
        "Execute a system command",
        "System Operations"
    ),
    AgentCommand.INSTALL_PACKAGE: CommandInfo(
        AgentCommand.INSTALL_PACKAGE,
        "Install a package or dependency",
        "System Operations"
    ),
    AgentCommand.SEARCH_FILES: CommandInfo(
        AgentCommand.SEARCH_FILES,
        "Search for files or content",
        "System Operations"
    ),

    # Agent operations
    AgentCommand.SHOW_HELP: CommandInfo(
        AgentCommand.SHOW_HELP,
        "Show help information",
        "Agent Operations"
    ),
    AgentCommand.SHOW_STATUS: CommandInfo(
        AgentCommand.SHOW_STATUS,
        "Show agent status and context",
        "Agent Operations"
    ),
    AgentCommand.CLEAR_CONTEXT: CommandInfo(
        AgentCommand.CLEAR_CONTEXT,
        "Clear the agent's context",
        "Agent Operations"
    ),
    AgentCommand.EXIT: CommandInfo(
        AgentCommand.EXIT,
        "Exit the agent",
        "Agent Operations"
    ),
}



def get_all_commands() -> List[CommandInfo]:
    """Get all commands as a list."""
    return list(COMMAND_INFO.values())
