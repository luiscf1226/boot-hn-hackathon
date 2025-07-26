"""
Project structure analysis functions for agent commands.
All functions return strings as they will be passed to the AI agent.
"""

import os
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict


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
    # First resolve the project_root itself using the same logic
    if project_root:
        project_root = project_root.strip()

        # Handle empty or current directory for project_root
        if not project_root or project_root == "." or project_root == "./":
            base_path = Path.cwd().resolve()
        else:
            root_path_obj = Path(project_root)

            # Apply same logic to project_root
            if root_path_obj.is_absolute():
                # Check if it's a real absolute system path
                if len(root_path_obj.parts) > 2 and (root_path_obj.exists() or str(root_path_obj).startswith(('/', 'C:', 'D:'))):
                    base_path = root_path_obj.resolve()
                else:
                    # Treat as relative to current directory (remove leading slash)
                    relative_part = str(root_path_obj).lstrip('/')
                    base_path = (Path.cwd() / relative_part).resolve()
            else:
                # Regular relative path
                base_path = (Path.cwd() / project_root).resolve()
    else:
        base_path = Path.cwd().resolve()

    input_path = input_path.strip()

    # Handle empty or current directory for input_path
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


def get_project_structure(project_root: str = None, max_depth: int = 5, ignore_patterns: List[str] = None) -> str:
    """
    Get recursive project structure as a tree string.

    Args:
        project_root: Project root directory (uses current dir if None)
        max_depth: Maximum depth to traverse
        ignore_patterns: Patterns to ignore (e.g., ['.git', '__pycache__', 'node_modules'])

    Returns:
        String representation of project structure
    """
    try:
        base_path = resolve_project_path(project_root or ".", None)

        if not base_path.exists():
            return f"Error: Directory '{base_path}' does not exist"

        if not base_path.is_dir():
            return f"Error: '{base_path}' is not a directory"

        # Default ignore patterns
        if ignore_patterns is None:
            ignore_patterns = [
                '.git', '.gitignore', '__pycache__', '.pyc',
                'node_modules', '.DS_Store', '.vscode', '.idea',
                'venv', 'env', '.env', 'dist', 'build'
            ]

        def should_ignore(path: Path) -> bool:
            """Check if path should be ignored."""
            path_str = str(path)
            path_name = path.name

            for pattern in ignore_patterns:
                if pattern in path_str or pattern in path_name:
                    return True
            return False

        def build_tree(path: Path, prefix: str = "", depth: int = 0) -> List[str]:
            """Build tree structure recursively."""
            if depth > max_depth or should_ignore(path):
                return []

            lines = []
            if depth == 0:
                lines.append(f"{path.name}/")

            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

                for i, item in enumerate(items):
                    if should_ignore(item):
                        continue

                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "

                    if item.is_dir():
                        lines.append(f"{prefix}{current_prefix}{item.name}/")
                        lines.extend(build_tree(item, prefix + next_prefix, depth + 1))
                    else:
                        # Show file with size
                        size = item.stat().st_size
                        size_str = format_file_size(size)
                        lines.append(f"{prefix}{current_prefix}{item.name} ({size_str})")

            except PermissionError:
                lines.append(f"{prefix}└── [Permission Denied]")

            return lines

        tree_lines = build_tree(base_path)
        result = f"Project structure for: {base_path}\n{'='*50}\n"
        result += "\n".join(tree_lines)

        return result

    except Exception as e:
        return f"Error analyzing project structure: {str(e)}"


def analyze_project_languages(project_root: str = None, ignore_patterns: List[str] = None) -> str:
    """
    Analyze programming languages and file types in the project.

    Args:
        project_root: Project root directory
        ignore_patterns: Patterns to ignore

    Returns:
        String with language analysis
    """
    try:
        base_path = resolve_project_path(project_root or ".", None)

        if not base_path.exists():
            return f"Error: Directory '{base_path}' does not exist"

        # Default ignore patterns
        if ignore_patterns is None:
            ignore_patterns = [
                '.git', '__pycache__', 'node_modules', '.DS_Store',
                'venv', 'env', 'dist', 'build'
            ]

        def should_ignore(path: Path) -> bool:
            path_str = str(path)
            for pattern in ignore_patterns:
                if pattern in path_str:
                    return True
            return False

        # Language mapping
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.json': 'JSON',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.sh': 'Shell Script',
            '.sql': 'SQL',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.r': 'R',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.dockerfile': 'Dockerfile',
            '.env': 'Environment',
            '.toml': 'TOML',
            '.xml': 'XML',
            '.vue': 'Vue.js'
        }

        file_stats = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
        total_files = 0
        total_size = 0

        for file_path in base_path.rglob('*'):
            if not file_path.is_file() or should_ignore(file_path):
                continue

            extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size

            # Special case for files without extension
            if not extension and file_path.name.lower() in ['dockerfile', 'makefile', 'readme']:
                extension = f'.{file_path.name.lower()}'

            language = language_map.get(extension, f'Other ({extension})' if extension else 'No Extension')

            file_stats[language]['count'] += 1
            file_stats[language]['size'] += file_size
            file_stats[language]['files'].append(str(file_path.relative_to(base_path)))

            total_files += 1
            total_size += file_size

        if not file_stats:
            return f"No files found in project '{base_path}'"

        # Sort by file count
        sorted_languages = sorted(file_stats.items(), key=lambda x: x[1]['count'], reverse=True)

        result = f"Project language analysis for: {base_path}\n"
        result += f"Total files: {total_files}, Total size: {format_file_size(total_size)}\n"
        result += "="*50 + "\n\n"

        for language, stats in sorted_languages:
            percentage = (stats['count'] / total_files) * 100
            size_str = format_file_size(stats['size'])
            result += f"{language}:\n"
            result += f"  Files: {stats['count']} ({percentage:.1f}%)\n"
            result += f"  Size: {size_str}\n"

            # Show some example files (up to 5)
            example_files = stats['files'][:5]
            result += f"  Examples: {', '.join(example_files)}"
            if len(stats['files']) > 5:
                result += f" (and {len(stats['files']) - 5} more)"
            result += "\n\n"

        return result

    except Exception as e:
        return f"Error analyzing project languages: {str(e)}"


def get_important_files(project_root: str = None) -> str:
    """
    Identify and analyze important project files (README, config files, etc.).

    Args:
        project_root: Project root directory

    Returns:
        String with important files analysis
    """
    try:
        base_path = resolve_project_path(project_root or ".", None)

        if not base_path.exists():
            return f"Error: Directory '{base_path}' does not exist"

        important_patterns = {
            'Documentation': ['readme*', 'changelog*', 'license*', 'authors*', 'contributors*'],
            'Configuration': ['*.json', '*.yml', '*.yaml', '*.toml', '*.ini', '*.cfg', '.env*'],
            'Build/Deploy': ['makefile', 'dockerfile*', '*.sh', 'requirements.txt', 'package.json', 'setup.py', 'pyproject.toml'],
            'Version Control': ['.gitignore', '.gitattributes'],
            'CI/CD': ['.github/**/*', '.gitlab-ci.yml', 'jenkinsfile*', '*.yml']
        }

        found_files = defaultdict(list)

        for category, patterns in important_patterns.items():
            for pattern in patterns:
                for file_path in base_path.glob(pattern):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(base_path)
                        file_size = file_path.stat().st_size
                        found_files[category].append({
                            'path': str(relative_path),
                            'size': file_size,
                            'full_path': file_path
                        })

        if not found_files:
            return f"No important files found in project '{base_path}'"

        result = f"Important files in project: {base_path}\n{'='*50}\n\n"

        for category, files in found_files.items():
            if files:
                result += f"{category}:\n"
                for file_info in sorted(files, key=lambda x: x['path']):
                    size_str = format_file_size(file_info['size'])
                    result += f"  - {file_info['path']} ({size_str})\n"
                result += "\n"

        return result

    except Exception as e:
        return f"Error analyzing important files: {str(e)}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def get_project_summary(project_root: str = None) -> str:
    """
    Get a comprehensive project summary combining structure, languages, and important files.

    Args:
        project_root: Project root directory

    Returns:
        String with complete project summary
    """
    try:
        base_path = resolve_project_path(project_root or ".", None)

        result = f"COMPREHENSIVE PROJECT SUMMARY\n"
        result += f"Project: {base_path}\n"
        result += "="*60 + "\n\n"

        # 1. Language Analysis
        result += "1. LANGUAGE ANALYSIS:\n"
        result += "-" * 30 + "\n"
        lang_analysis = analyze_project_languages(str(base_path))
        if not lang_analysis.startswith("Error"):
            # Extract just the stats part
            lines = lang_analysis.split('\n')
            stats_start = False
            for line in lines:
                if '=' in line and stats_start:
                    break
                if '=' in line:
                    stats_start = True
                    continue
                if stats_start and line.strip():
                    result += line + "\n"
        else:
            result += lang_analysis + "\n"
        result += "\n"

        # 2. Important Files
        result += "2. IMPORTANT FILES:\n"
        result += "-" * 30 + "\n"
        important_files = get_important_files(str(base_path))
        if not important_files.startswith("Error"):
            # Extract just the files part
            lines = important_files.split('\n')
            files_start = False
            for line in lines:
                if '=' in line:
                    files_start = True
                    continue
                if files_start and line.strip():
                    result += line + "\n"
        else:
            result += important_files + "\n"
        result += "\n"

        # 3. Directory Structure (simplified)
        result += "3. PROJECT STRUCTURE:\n"
        result += "-" * 30 + "\n"
        structure = get_project_structure(str(base_path), max_depth=3)  # Limit depth for summary
        if not structure.startswith("Error"):
            # Extract just the tree part
            lines = structure.split('\n')
            tree_start = False
            for line in lines:
                if '=' in line:
                    tree_start = True
                    continue
                if tree_start:
                    result += line + "\n"
        else:
            result += structure + "\n"

        return result

    except Exception as e:
        return f"Error creating project summary: {str(e)}"
