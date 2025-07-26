"""
Explain command implementation for AI-powered code explanation.
"""

import os
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.commands.base import BaseCommand, CommandResult
from app.models.user import User
from app.services.agent import Agent


class ExplainCommand(BaseCommand):
    """Command for AI-powered code explanation."""

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    async def execute(self, action: str = None, **kwargs) -> Dict[str, Any]:
        """Execute the explain command."""
        if action == "analyze_file":
            return await self._analyze_file(kwargs.get("file_path", ""))
        elif action == "analyze_code":
            return await self._analyze_code(kwargs.get("code", ""))
        elif action == "analyze_current_dir":
            return await self._analyze_current_directory()
        else:
            # Default: ask user what they want to explain
            return await self._prompt_for_input()

    async def _prompt_for_input(self) -> Dict[str, Any]:
        """Prompt user for what they want to explain."""
        return {
            "success": True,
            "message": "What would you like me to explain?",
            "prompt": "explain_input",
            "data": {
                "options": [
                    {"key": "paste", "desc": "Paste code to analyze"},
                    {"key": "file", "desc": "Analyze a specific file"},
                    {"key": "current", "desc": "Analyze current directory structure"},
                ]
            }
        }

    async def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze pasted code."""
        try:
            if not code.strip():
                return CommandResult(False, "No code provided to analyze").to_dict()

            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "No API key found. Please run /setup first to configure your Gemini API key for AI code explanation."
                ).to_dict()

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session("Code Explanation")
            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Create comprehensive system prompt for code explanation
            system_prompt = """You are an expert software engineer and code mentor. Your job is to analyze and explain code in a clear, educational manner.

When explaining code, provide:

## 📋 Code Overview
- Brief summary of what this code does
- Primary purpose and functionality
- Programming language and key technologies used

## 🏗️ Structure Analysis
- Main components, classes, functions, or modules
- How different parts work together
- Data flow and control flow

## 🔍 Line-by-Line Breakdown
- Explain complex or important sections
- Highlight key algorithms or logic
- Point out design patterns used

## 💡 Key Concepts
- Important programming concepts demonstrated
- Best practices shown (or missing)
- Common patterns or techniques used

## 🚀 How It Works
- Step-by-step execution flow
- Input and output behavior
- Side effects or dependencies

## ⚠️ Potential Issues
- Code smells or anti-patterns
- Security considerations
- Performance implications
- Areas for improvement

## 🎯 Learning Points
- What beginners can learn from this code
- Advanced concepts demonstrated
- Takeaways for better coding

Be thorough but accessible. Use examples and analogies when helpful. Focus on education and understanding."""

            user_message = f"""Please analyze and explain this code:

```
{code}
```

Provide a comprehensive explanation that helps understand what this code does, how it works, and what can be learned from it."""

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI code explanation failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Clean up the AI response
            explanation_content = ai_response["response"].strip()

            # Return the explanation
            return {
                "success": True,
                "message": "🤖 AI Code Explanation Complete:",
                "explanation_content": explanation_content,
                "code_analyzed": code[:200] + "..." if len(code) > 200 else code,
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown"),
                "analysis_type": "pasted_code"
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Code analysis failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    async def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a specific file."""
        try:
            if not file_path.strip():
                return CommandResult(False, "No file path provided").to_dict()

            # Resolve relative path
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Check if file exists
            if not os.path.exists(file_path):
                return CommandResult(False, f"File not found: {file_path}").to_dict()

            # Check if it's actually a file
            if not os.path.isfile(file_path):
                return CommandResult(False, f"Path is not a file: {file_path}").to_dict()

            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        file_content = f.read()
                except Exception as e:
                    return CommandResult(False, f"Could not read file {file_path}: {str(e)}").to_dict()
            except Exception as e:
                return CommandResult(False, f"Could not read file {file_path}: {str(e)}").to_dict()

            # Check file size (limit to reasonable size for analysis)
            if len(file_content) > 50000:  # 50KB limit
                return CommandResult(False, f"File too large for analysis (max 50KB). File size: {len(file_content)} characters").to_dict()

            # Get file info
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]

            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "No API key found. Please run /setup first to configure your Gemini API key for AI code explanation."
                ).to_dict()

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                agent.start_new_session(f"File Analysis: {file_name}")
            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Create file-specific system prompt
            system_prompt = """You are an expert software engineer analyzing a source code file. Provide a comprehensive analysis and explanation.

Structure your analysis as follows:

## 📁 File Overview
- File name, type, and purpose
- Programming language and framework/library used
- Role in the larger project/system

## 🏗️ Architecture & Structure
- Main components (classes, functions, modules)
- Imports and dependencies
- Overall organization and patterns

## 🔍 Detailed Analysis
- Key functions/methods and their purposes
- Important algorithms or logic
- Data structures and their usage
- Design patterns implemented

## 🔄 Flow & Interactions
- How the code executes
- Entry points and main workflows
- Interactions with external systems/files
- Data processing pipeline

## 💡 Code Quality & Practices
- Good practices demonstrated
- Code style and organization
- Error handling approach
- Documentation quality

## ⚠️ Areas of Interest
- Complex or clever implementations
- Potential issues or improvements
- Security considerations
- Performance implications

## 🎯 Key Takeaways
- What this file teaches about good coding
- Concepts that can be applied elsewhere
- Learning opportunities for developers

Be specific and reference actual code snippets when helpful."""

            user_message = f"""Please analyze this file:

**File:** {file_path}
**Name:** {file_name}
**Extension:** {file_extension}
**Size:** {len(file_content)} characters

**Content:**
```
{file_content}
```

Provide a thorough analysis explaining what this file does, how it's structured, and what can be learned from it."""

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI file analysis failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Clean up the AI response
            explanation_content = ai_response["response"].strip()

            # Return the explanation
            return {
                "success": True,
                "message": f"🤖 AI File Analysis Complete for {file_name}:",
                "explanation_content": explanation_content,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": len(file_content),
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown"),
                "analysis_type": "file_analysis"
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"File analysis failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    async def _analyze_current_directory(self) -> Dict[str, Any]:
        """Analyze current directory structure."""
        try:
            current_dir = os.getcwd()

            # Get directory structure (limited depth to avoid huge outputs)
            dir_structure = self._get_directory_structure(current_dir, max_depth=3)

            # Get key files for analysis
            key_files = self._identify_key_files(current_dir)

            # Check if user has API key configured
            user = User.get_or_create_default_user(self.db)
            if not user.gemini_api_key:
                return CommandResult(False,
                    "No API key found. Please run /setup first to configure your Gemini API key for AI code explanation."
                ).to_dict()

            # Initialize AI agent
            try:
                agent = Agent(self.db)
                project_name = os.path.basename(current_dir)
                agent.start_new_session(f"Directory Analysis: {project_name}")
            except Exception as e:
                return CommandResult(False, f"Failed to initialize AI agent: {str(e)}").to_dict()

            # Create directory analysis system prompt
            system_prompt = """You are an expert software architect analyzing a project directory structure. Provide insights about the project organization, architecture, and purpose.

Structure your analysis as follows:

## Project Overview
- Project name and apparent purpose
- Technology stack and framework used
- Project type (web app, library, CLI tool, etc.)

## Architecture Analysis
- Directory structure and organization patterns
- Separation of concerns
- Architectural patterns (MVC, microservices, etc.)
- Configuration and setup files

## Key Components
- Main application directories and their purposes
- Important configuration files
- Build and deployment files
- Documentation and testing structure

## Code Organization
- How code is structured and modularized
- Naming conventions and patterns
- Dependencies and external libraries
- Development vs production concerns

## Best Practices Observed
- Good organizational patterns
- Standard conventions followed
- Professional development practices
- Documentation quality

## Potential Issues
- Missing standard files or directories
- Organizational concerns
- Suggestions for improvement
- Standard patterns not followed

## Development Insights
- What this project structure teaches
- How developers can learn from this organization
- Patterns to adopt or avoid

Be specific about what you observe in the directory structure."""

            user_message = f"""Please analyze this project directory:

**Current Directory:** {current_dir}
**Project Name:** {os.path.basename(current_dir)}

**Directory Structure:**
{dir_structure}

**Key Files Found:**
{key_files}

Analyze the project structure, identify the technology stack, architectural patterns, and provide insights about how this project is organized."""

            # Send to AI
            try:
                ai_response = await agent.send_system_message(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    save_to_db=True
                )

                if not ai_response["success"]:
                    return CommandResult(False, f"AI directory analysis failed: {ai_response.get('error', 'Unknown error')}").to_dict()

            except Exception as e:
                return CommandResult(False, f"AI service error: {str(e)}").to_dict()

            # Clean up the AI response
            explanation_content = ai_response["response"].strip()

            # Return the explanation
            return {
                "success": True,
                "message": f"AI Directory Analysis Complete for {os.path.basename(current_dir)}:",
                "explanation_content": explanation_content,
                "directory_path": current_dir,
                "directory_structure": dir_structure,
                "ai_model": ai_response.get("model", "Unknown"),
                "session_id": ai_response.get("session_id", "Unknown"),
                "analysis_type": "directory_analysis"
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return CommandResult(False, f"Directory analysis failed: {str(e)}\n\nDetails: {error_detail}").to_dict()

    def _get_directory_structure(self, path: str, max_depth: int = 3, current_depth: int = 0) -> str:
        """Get directory structure as a string."""
        if current_depth >= max_depth:
            return ""

        structure = []
        try:
            items = sorted(os.listdir(path))
            for item in items:
                # Skip hidden files and common unimportant directories
                if item.startswith('.') or item in ['__pycache__', 'node_modules', '.git', 'venv', 'env']:
                    continue

                item_path = os.path.join(path, item)
                indent = "  " * current_depth

                if os.path.isdir(item_path):
                    structure.append(f"{indent}{item}/")
                    if current_depth < max_depth - 1:
                        sub_structure = self._get_directory_structure(item_path, max_depth, current_depth + 1)
                        if sub_structure:
                            structure.append(sub_structure)
                else:
                    structure.append(f"{indent}{item}")
        except PermissionError:
            structure.append(f"{'  ' * current_depth}[Permission Denied]")

        return "\n".join(structure)

    def _identify_key_files(self, path: str) -> str:
        """Identify key project files."""
        key_files = []
        important_files = [
            'README.md', 'README.txt', 'README',
            'package.json', 'requirements.txt', 'Pipfile', 'setup.py', 'pyproject.toml',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'Makefile', '.gitignore', 'LICENSE', 'LICENSE.txt',
            'main.py', 'app.py', 'index.js', 'index.html',
            'config.py', 'settings.py', 'config.json',
            '.env.example', 'env.example'
        ]

        try:
            for root, dirs, files in os.walk(path):
                # Only check root and first level directories
                if root.count(os.sep) - path.count(os.sep) > 1:
                    continue

                for file in files:
                    if file in important_files:
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        key_files.append(f"- {rel_path}")

                # Stop descending into hidden or unimportant directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
        except Exception:
            pass

        return "\n".join(key_files) if key_files else "- No standard project files found"

    def get_help(self) -> str:
        """Get help text for the explain command."""
        return """Explain Command Help
===================

The 'explain' command provides AI-powered code explanation and analysis.

How it works:
1. Analyzes code, files, or project structure
2. Uses AI to provide comprehensive explanations
3. Breaks down complex concepts into understandable parts
4. Provides learning insights and best practices

Usage Options:

/explain                    # Interactive mode - choose what to analyze
/explain paste <code>       # Analyze pasted code
/explain file <path>        # Analyze specific file
/explain current           # Analyze current directory structure

File Analysis:
- Analyzes file structure, purpose, and implementation
- Explains algorithms, patterns, and techniques used
- Identifies learning opportunities and best practices
- Supports most programming languages

Directory Analysis:
- Examines project structure and organization
- Identifies technology stack and architectural patterns
- Analyzes configuration and setup files
- Provides insights about project organization

Code Analysis Features:
- Line-by-line breakdown of complex logic
- Explanation of design patterns and algorithms
- Security and performance considerations
- Best practices and potential improvements
- Educational insights for learning

Prerequisites:
- Set GEMINI_API_KEY in your .env file
- Run /setup to configure your AI model

Examples:
/explain                                    # Choose analysis type
/explain file ./main.py                     # Analyze main.py file
/explain current                           # Analyze current project
/explain paste "def factorial(n): ..."     # Analyze pasted code

Note: File analysis limited to 50KB files for performance."""
