"""
Code analysis functions for understanding and analyzing code structure.
All functions return strings as they will be passed to the AI agent.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
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
                if len(root_path_obj.parts) > 2 and (
                    root_path_obj.exists()
                    or str(root_path_obj).startswith(("/", "C:", "D:"))
                ):
                    base_path = root_path_obj.resolve()
                else:
                    # Treat as relative to current directory (remove leading slash)
                    relative_part = str(root_path_obj).lstrip("/")
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
        if len(path_obj.parts) > 2 and (
            path_obj.exists() or str(path_obj).startswith(("/", "C:", "D:"))
        ):
            return path_obj.resolve()
        else:
            # Treat as relative to project root (remove leading slash)
            relative_part = str(path_obj).lstrip("/")
            return (base_path / relative_part).resolve()
    else:
        # Regular relative path
        return (base_path / input_path).resolve()


def analyze_python_file(file_path: str, project_root: str = None) -> str:
    """
    Analyze a Python file for structure, complexity, and patterns.

    Args:
        file_path: Path to the Python file
        project_root: Project root directory

    Returns:
        String with detailed analysis
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        if not full_path.exists():
            return f"Error: File '{full_path}' does not exist"

        if not full_path.is_file():
            return f"Error: '{full_path}' is not a file"

        if full_path.suffix.lower() != ".py":
            return f"Error: '{full_path}' is not a Python file"

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Parse AST
        try:
            tree = ast.parse(content, filename=str(full_path))
        except SyntaxError as e:
            return f"Syntax Error in {full_path}: {e}"

        # Analyze structure
        analyzer = PythonCodeAnalyzer()
        analysis = analyzer.analyze(tree, content)

        # Show relative path for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = full_path.relative_to(base_path)
        except ValueError:
            display_path = full_path

        result = f"Python Code Analysis: {display_path}\n"
        result += "=" * 50 + "\n\n"

        # File metrics
        lines = content.split("\n")
        result += f"📊 File Metrics:\n"
        result += f"  Lines of code: {len(lines)}\n"
        result += f"  File size: {len(content)} characters\n"
        result += f"  Blank lines: {sum(1 for line in lines if not line.strip())}\n"
        result += f"  Comment lines: {sum(1 for line in lines if line.strip().startswith('#'))}\n\n"

        # Structure analysis
        result += f"🏗️  Code Structure:\n"
        result += f"  Functions: {len(analysis['functions'])}\n"
        result += f"  Classes: {len(analysis['classes'])}\n"
        result += f"  Imports: {len(analysis['imports'])}\n"
        result += f"  Global variables: {len(analysis['globals'])}\n\n"

        # Detailed breakdown
        if analysis["imports"]:
            result += f"📦 Imports:\n"
            for imp in analysis["imports"][:10]:  # Show first 10
                result += f"  - {imp}\n"
            if len(analysis["imports"]) > 10:
                result += f"  ... and {len(analysis['imports']) - 10} more\n"
            result += "\n"

        if analysis["classes"]:
            result += f"🏛️  Classes:\n"
            for cls in analysis["classes"]:
                result += f"  - {cls['name']} (line {cls['line']}, {cls['methods']} methods)\n"
            result += "\n"

        if analysis["functions"]:
            result += f"⚙️  Functions:\n"
            for func in analysis["functions"][:10]:  # Show first 10
                result += (
                    f"  - {func['name']}() (line {func['line']}, {func['args']} args)\n"
                )
            if len(analysis["functions"]) > 10:
                result += f"  ... and {len(analysis['functions']) - 10} more\n"
            result += "\n"

        # Complexity analysis
        result += f"⚡ Complexity Analysis:\n"
        result += (
            f"  Average function length: {analysis['avg_function_length']:.1f} lines\n"
        )
        result += f"  Max function length: {analysis['max_function_length']} lines\n"
        result += f"  Cyclomatic complexity: {analysis['cyclomatic_complexity']}\n\n"

        # Code quality insights
        if analysis["insights"]:
            result += f"💡 Code Quality Insights:\n"
            for insight in analysis["insights"]:
                result += f"  - {insight}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"Error analyzing Python file '{file_path}': {str(e)}"


def analyze_directory_code(
    directory: str, project_root: str = None, file_extensions: List[str] = None
) -> str:
    """
    Analyze code files in a directory for patterns and structure.

    Args:
        directory: Directory to analyze
        project_root: Project root directory
        file_extensions: File extensions to analyze (default: ['.py', '.js', '.ts'])

    Returns:
        String with directory code analysis
    """
    try:
        search_path = resolve_project_path(directory, project_root)

        if not search_path.exists():
            return f"Error: Directory '{search_path}' does not exist"

        if not search_path.is_dir():
            return f"Error: '{search_path}' is not a directory"

        if file_extensions is None:
            file_extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]

        # Get base path for relative display
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = search_path.relative_to(base_path)
        except ValueError:
            display_path = search_path

        result = f"Code Analysis for Directory: {display_path}\n"
        result += "=" * 50 + "\n\n"

        # Collect files
        code_files = []
        for ext in file_extensions:
            code_files.extend(search_path.rglob(f"*{ext}"))

        if not code_files:
            return f"No code files found in directory '{search_path}'"

        # Analyze each file type
        stats_by_ext = defaultdict(
            lambda: {
                "count": 0,
                "total_lines": 0,
                "total_size": 0,
                "functions": 0,
                "classes": 0,
                "files": [],
            }
        )

        total_files = 0
        for file_path in code_files:
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            file_size = file_path.stat().st_size

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = len(content.split("\n"))

                # Basic analysis
                stats_by_ext[ext]["count"] += 1
                stats_by_ext[ext]["total_lines"] += lines
                stats_by_ext[ext]["total_size"] += file_size

                try:
                    relative_path = file_path.relative_to(base_path)
                except ValueError:
                    relative_path = file_path

                stats_by_ext[ext]["files"].append(str(relative_path))

                # Language-specific analysis
                if ext == ".py":
                    try:
                        tree = ast.parse(content)
                        analyzer = PythonCodeAnalyzer()
                        analysis = analyzer.analyze(tree, content)
                        stats_by_ext[ext]["functions"] += len(analysis["functions"])
                        stats_by_ext[ext]["classes"] += len(analysis["classes"])
                    except:
                        pass

                total_files += 1

            except Exception:
                continue

        # Generate report
        result += f"📊 Summary:\n"
        result += f"  Total code files: {total_files}\n"
        result += f"  File types: {len(stats_by_ext)}\n\n"

        for ext, stats in sorted(stats_by_ext.items()):
            if stats["count"] == 0:
                continue

            result += f"📄 {ext.upper()} Files:\n"
            result += f"  Count: {stats['count']}\n"
            result += f"  Total lines: {stats['total_lines']}\n"
            result += f"  Average lines per file: {stats['total_lines'] / stats['count']:.1f}\n"
            result += f"  Total size: {format_file_size(stats['total_size'])}\n"

            if ext == ".py" and (stats["functions"] > 0 or stats["classes"] > 0):
                result += f"  Functions: {stats['functions']}\n"
                result += f"  Classes: {stats['classes']}\n"

            result += f"  Files: {', '.join(stats['files'][:5])}"
            if len(stats["files"]) > 5:
                result += f" (and {len(stats['files']) - 5} more)"
            result += "\n\n"

        return result

    except Exception as e:
        return f"Error analyzing directory code '{directory}': {str(e)}"


def find_code_patterns(
    file_path: str, patterns: List[str], project_root: str = None
) -> str:
    """
    Find specific code patterns in a file using regex.

    Args:
        file_path: Path to the file
        patterns: List of regex patterns to search for
        project_root: Project root directory

    Returns:
        String with pattern matches
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        if not full_path.exists():
            return f"Error: File '{full_path}' does not exist"

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
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

        result = f"Code Pattern Search in: {display_path}\n"
        result += "=" * 50 + "\n\n"

        lines = content.split("\n")
        total_matches = 0

        for pattern in patterns:
            try:
                regex = re.compile(pattern, re.MULTILINE)
                matches = []

                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append(f"  Line {line_num}: {line.strip()}")

                if matches:
                    result += f"🔍 Pattern '{pattern}':\n"
                    result += "\n".join(matches[:10])  # Show first 10 matches
                    if len(matches) > 10:
                        result += f"\n  ... and {len(matches) - 10} more matches"
                    result += "\n\n"
                    total_matches += len(matches)
                else:
                    result += f"❌ Pattern '{pattern}': No matches\n\n"

            except re.error as e:
                result += f"❌ Invalid pattern '{pattern}': {e}\n\n"

        result += f"Total matches found: {total_matches}\n"
        return result

    except Exception as e:
        return f"Error searching for patterns in '{file_path}': {str(e)}"


def analyze_dependencies(file_path: str, project_root: str = None) -> str:
    """
    Analyze dependencies and imports in a code file.

    Args:
        file_path: Path to the file
        project_root: Project root directory

    Returns:
        String with dependency analysis
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        if not full_path.exists():
            return f"Error: File '{full_path}' does not exist"

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
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

        result = f"Dependency Analysis: {display_path}\n"
        result += "=" * 50 + "\n\n"

        ext = full_path.suffix.lower()

        if ext == ".py":
            # Python dependencies
            deps = analyze_python_dependencies(content)
        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            # JavaScript/TypeScript dependencies
            deps = analyze_js_dependencies(content)
        else:
            return f"Dependency analysis not supported for {ext} files"

        if not deps["imports"]:
            return f"No dependencies found in {display_path}"

        result += f"📦 Dependencies Summary:\n"
        result += f"  Total imports: {len(deps['imports'])}\n"
        result += f"  External packages: {len(deps['external'])}\n"
        result += f"  Local imports: {len(deps['local'])}\n"
        result += f"  Standard library: {len(deps['stdlib'])}\n\n"

        if deps["external"]:
            result += f"🌐 External Packages:\n"
            for pkg in sorted(deps["external"]):
                result += f"  - {pkg}\n"
            result += "\n"

        if deps["local"]:
            result += f"🏠 Local Imports:\n"
            for imp in sorted(deps["local"]):
                result += f"  - {imp}\n"
            result += "\n"

        if deps["stdlib"]:
            result += f"📚 Standard Library:\n"
            for lib in sorted(deps["stdlib"]):
                result += f"  - {lib}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"Error analyzing dependencies in '{file_path}': {str(e)}"


class PythonCodeAnalyzer:
    """Helper class for analyzing Python AST."""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.globals = []
        self.complexity = 0

    def analyze(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze Python AST and return structured information."""
        self.visit(tree)

        lines = content.split("\n")
        function_lengths = [func.get("length", 0) for func in self.functions]

        insights = []
        if len(self.functions) > 20:
            insights.append(
                "Large number of functions - consider splitting into modules"
            )
        if any(length > 50 for length in function_lengths):
            insights.append(
                "Some functions are very long - consider breaking them down"
            )
        if len(self.imports) > 30:
            insights.append("Many imports - check if all are necessary")
        if self.complexity > 50:
            insights.append("High cyclomatic complexity - consider refactoring")

        return {
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "globals": self.globals,
            "avg_function_length": sum(function_lengths) / len(function_lengths)
            if function_lengths
            else 0,
            "max_function_length": max(function_lengths) if function_lengths else 0,
            "cyclomatic_complexity": self.complexity,
            "insights": insights,
        }

    def visit(self, node: ast.AST):
        """Visit AST nodes recursively."""
        if isinstance(node, ast.FunctionDef):
            self.functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args),
                    "length": getattr(node, "end_lineno", node.lineno) - node.lineno,
                }
            )
            self.complexity += self._calculate_complexity(node)

        elif isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            self.classes.append(
                {"name": node.name, "line": node.lineno, "methods": len(methods)}
            )

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)
            else:
                module = node.module or ""
                for alias in node.names:
                    self.imports.append(
                        f"{module}.{alias.name}" if module else alias.name
                    )

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.globals.append(target.id)

        # Continue visiting child nodes
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.AsyncFor,
                    ast.ExceptHandler,
                    ast.With,
                    ast.AsyncWith,
                ),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


def analyze_python_dependencies(content: str) -> Dict[str, List[str]]:
    """Analyze Python dependencies from source code."""
    try:
        tree = ast.parse(content)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])

        # Categorize imports
        python_stdlib = {
            "os",
            "sys",
            "json",
            "urllib",
            "http",
            "datetime",
            "time",
            "re",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "subprocess",
            "threading",
            "multiprocessing",
            "asyncio",
            "logging",
            "unittest",
            "sqlite3",
            "csv",
            "xml",
            "html",
            "email",
            "base64",
            "hashlib",
        }

        external = []
        local = []
        stdlib = []

        for imp in set(imports):
            if imp in python_stdlib:
                stdlib.append(imp)
            elif imp.startswith(".") or "/" in imp:
                local.append(imp)
            else:
                external.append(imp)

        return {
            "imports": imports,
            "external": external,
            "local": local,
            "stdlib": stdlib,
        }

    except Exception:
        return {"imports": [], "external": [], "local": [], "stdlib": []}


def analyze_js_dependencies(content: str) -> Dict[str, List[str]]:
    """Analyze JavaScript/TypeScript dependencies from source code."""
    import_patterns = [
        r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
        r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
    ]

    imports = []
    for pattern in import_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        imports.extend(matches)

    # Categorize imports
    external = []
    local = []

    for imp in set(imports):
        if imp.startswith("./") or imp.startswith("../") or imp.startswith("/"):
            local.append(imp)
        else:
            external.append(imp)

    return {
        "imports": imports,
        "external": external,
        "local": local,
        "stdlib": [],  # JS doesn't have a standard library like Python
    }


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
