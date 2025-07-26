"""
File operations functions for agent commands.
All functions return strings (including errors) as they will be passed to the AI agent.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def resolve_project_path(input_path: str, project_root: str = None) -> Path:
    """
    Resolve a path relative to the project root, handling various input formats.

    Args:
        input_path: Input path that can be:
                   - Absolute system path (/Users/name/project/file.py)
                   - Relative to project root (/src/main.py -> project_root/src/main.py)
                   - Relative path (src/main.py -> project_root/src/main.py)
                   - Current directory (. or empty)
        project_root: Project root directory (uses current dir if None)

    Returns:
        Path object with resolved path
    """
    if project_root:
        base_path = Path(project_root).resolve()
    else:
        base_path = Path.cwd().resolve()

    input_path = input_path.strip()

    # Handle empty or current directory
    if not input_path or input_path == "." or input_path == "./":
        return base_path

    path_obj = Path(input_path)

    # Check if it's a real absolute system path (has multiple parts and exists or looks like system path)
    if path_obj.is_absolute():
        # If it starts with system root and has multiple parts, treat as absolute
        if len(path_obj.parts) > 2 and (path_obj.exists() or str(path_obj).startswith(('/', 'C:', 'D:'))):
            return path_obj.resolve()
        else:
            # Treat as relative to project root (remove leading slash)
            relative_part = str(path_obj).lstrip('/')
            return (base_path / relative_part).resolve()
    else:
        # Regular relative path
        return (base_path / input_path).resolve()


def read_file(file_path: str, project_root: str = None) -> str:
    """
    Read contents of a file and return as string.

    Args:
        file_path: Path to the file (relative to project, absolute, or starting with /)
        project_root: Project root directory (uses current dir if None)

    Returns:
        String containing file contents or error message
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        if not full_path.exists():
            return f"Error: File '{full_path}' does not exist"

        if not full_path.is_file():
            return f"Error: '{full_path}' is not a file"

        # Check file size (avoid reading huge files)
        file_size = full_path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return f"Error: File '{full_path}' is too large ({file_size} bytes). Maximum size is 10MB."

        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Show relative path for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = full_path.relative_to(base_path)
        except ValueError:
            display_path = full_path

        return f"File: {display_path}\n{'='*50}\n{content}"

    except PermissionError:
        return f"Error: Permission denied reading '{file_path}'"
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"


def search_in_file(file_path: str, pattern: str, project_root: str = None, case_sensitive: bool = False) -> str:
    """
    Search for a pattern in a file (like grep).

    Args:
        file_path: Path to the file
        pattern: Search pattern (regex supported)
        project_root: Project root directory
        case_sensitive: Whether search is case sensitive

    Returns:
        String with matching lines or error message
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        if not full_path.exists():
            return f"Error: File '{full_path}' does not exist"

        if not full_path.is_file():
            return f"Error: '{full_path}' is not a file"

        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)

        matches = []
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if regex.search(line):
                    matches.append(f"{line_num}: {line.rstrip()}")

        if not matches:
            return f"No matches found for pattern '{pattern}' in '{full_path}'"

        # Show relative path for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = full_path.relative_to(base_path)
        except ValueError:
            display_path = full_path

        result = f"Search results for '{pattern}' in {display_path}:\n{'='*50}\n"
        result += "\n".join(matches)
        return result

    except re.error as e:
        return f"Error: Invalid regex pattern '{pattern}': {str(e)}"
    except Exception as e:
        return f"Error searching in file '{file_path}': {str(e)}"


def search_in_directory(directory: str, pattern: str, file_extensions: List[str] = None, project_root: str = None, case_sensitive: bool = False, max_files: int = 100) -> str:
    """
    Search for a pattern in multiple files in a directory (like grep -r).

    Args:
        directory: Directory to search in
        pattern: Search pattern
        file_extensions: List of file extensions to search (e.g., ['.py', '.js'])
        project_root: Project root directory
        case_sensitive: Whether search is case sensitive
        max_files: Maximum number of files to search

    Returns:
        String with search results or error message
    """
    try:
        search_path = resolve_project_path(directory, project_root)

        if not search_path.exists():
            return f"Error: Directory '{search_path}' does not exist"

        if not search_path.is_dir():
            return f"Error: '{search_path}' is not a directory"

        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)

        results = []
        files_searched = 0

        # Get base path for relative display
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        for file_path in search_path.rglob('*'):
            if files_searched >= max_files:
                results.append(f"\n--- Stopped after searching {max_files} files ---")
                break

            if not file_path.is_file():
                continue

            # Filter by extensions if provided
            if file_extensions and file_path.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                continue

            # Skip binary files and large files
            try:
                if file_path.stat().st_size > 1024 * 1024:  # 1MB limit for search
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            try:
                                relative_path = file_path.relative_to(base_path)
                            except ValueError:
                                relative_path = file_path
                            results.append(f"{relative_path}:{line_num}: {line.rstrip()}")

                files_searched += 1

            except (PermissionError, UnicodeDecodeError):
                continue

        if not results:
            return f"No matches found for pattern '{pattern}' in directory '{search_path}'"

        try:
            display_path = search_path.relative_to(base_path)
        except ValueError:
            display_path = search_path

        header = f"Search results for '{pattern}' in {display_path}:\n"
        header += f"Searched {files_searched} files\n{'='*50}\n"
        return header + "\n".join(results)

    except re.error as e:
        return f"Error: Invalid regex pattern '{pattern}': {str(e)}"
    except Exception as e:
        return f"Error searching in directory '{directory}': {str(e)}"


def create_file(file_path: str, content: str, project_root: str = None, overwrite: bool = False) -> str:
    """
    Create a file with given content.

    Args:
        file_path: Path for the new file
        content: Content to write to the file
        project_root: Project root directory
        overwrite: Whether to overwrite existing files

    Returns:
        Success message or error string
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        # Check if file already exists
        if full_path.exists() and not overwrite:
            return f"Error: File '{full_path}' already exists. Use overwrite=True to replace it."

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully created file: {full_path}"

    except PermissionError:
        return f"Error: Permission denied creating file '{file_path}'"
    except Exception as e:
        return f"Error creating file '{file_path}': {str(e)}"


def list_files(directory: str = ".", file_extensions: List[str] = None, project_root: str = None, recursive: bool = True, max_files: int = 500) -> str:
    """
    List files in a directory with optional filtering.

    Args:
        directory: Directory to list (default current directory)
        file_extensions: Filter by file extensions
        project_root: Project root directory
        recursive: Whether to search recursively
        max_files: Maximum number of files to list

    Returns:
        String with file list or error message
    """
    try:
        search_path = resolve_project_path(directory, project_root)

        if not search_path.exists():
            return f"Error: Directory '{search_path}' does not exist"

        if not search_path.is_dir():
            return f"Error: '{search_path}' is not a directory"

        files = []
        files_count = 0

        # Get base path for relative display
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'

        for file_path in search_path.glob(pattern):
            if files_count >= max_files:
                files.append(f"\n--- Stopped after listing {max_files} files ---")
                break

            if file_path.is_file():
                # Filter by extensions if provided
                if file_extensions and file_path.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

                try:
                    relative_path = file_path.relative_to(base_path)
                except ValueError:
                    relative_path = file_path

                file_size = file_path.stat().st_size
                files.append(f"{relative_path} ({file_size} bytes)")
                files_count += 1

        if not files:
            return f"No files found in directory '{search_path}'"

        try:
            display_path = search_path.relative_to(base_path)
        except ValueError:
            display_path = search_path

        header = f"Files in {display_path}:\n{'='*50}\n"
        return header + "\n".join(files)

    except Exception as e:
        return f"Error listing files in directory '{directory}': {str(e)}"
