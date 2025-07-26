"""
Code generation functions for creating and scaffolding code.
All functions return strings as they will be passed to the AI agent.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


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


def generate_python_class(class_name: str, file_path: str, project_root: str = None,
                         methods: List[str] = None, parent_class: str = None,
                         docstring: str = None) -> str:
    """
    Generate a Python class template and save to file.

    Args:
        class_name: Name of the class
        file_path: Path where to save the class file
        project_root: Project root directory
        methods: List of method names to include
        parent_class: Parent class name for inheritance
        docstring: Class docstring

    Returns:
        String with generation result
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate class code
        code = f'"""\n{class_name} module.\n"""\n\n'

        # Add imports if needed
        if parent_class and '.' in parent_class:
            module, cls = parent_class.rsplit('.', 1)
            code += f"from {module} import {cls}\n\n"
            parent_class = cls

        # Class definition
        inheritance = f"({parent_class})" if parent_class else ""
        code += f"class {class_name}{inheritance}:\n"

        # Add docstring
        if docstring:
            code += f'    """{docstring}"""\n\n'
        else:
            code += f'    """{class_name} class."""\n\n'

        # Constructor
        code += "    def __init__(self):\n"
        if parent_class:
            code += "        super().__init__()\n"
        code += "        pass\n\n"

        # Add methods
        if methods:
            for method in methods:
                code += f"    def {method}(self):\n"
                code += f'        """TODO: Implement {method} method."""\n'
                code += "        pass\n\n"
        else:
            # Add a default method
            code += "    def example_method(self):\n"
            code += '        """Example method."""\n'
            code += "        pass\n"

        # Write to file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(code)

        # Show relative path for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = full_path.relative_to(base_path)
        except ValueError:
            display_path = full_path

        return f"✅ Successfully generated Python class '{class_name}' in {display_path}"

    except Exception as e:
        return f"❌ Error generating Python class: {str(e)}"


def generate_python_function(function_name: str, file_path: str, project_root: str = None,
                           parameters: List[str] = None, return_type: str = None,
                           docstring: str = None, async_func: bool = False) -> str:
    """
    Generate a Python function template and save to file.

    Args:
        function_name: Name of the function
        file_path: Path where to save the function
        project_root: Project root directory
        parameters: List of parameter names
        return_type: Return type annotation
        docstring: Function docstring
        async_func: Whether to create an async function

    Returns:
        String with generation result
    """
    try:
        full_path = resolve_project_path(file_path, project_root)

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists and read current content
        existing_content = ""
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # Generate function code
        func_keyword = "async def" if async_func else "def"
        params = ", ".join(parameters) if parameters else ""
        return_annotation = f" -> {return_type}" if return_type else ""

        code = f"{func_keyword} {function_name}({params}){return_annotation}:\n"

        # Add docstring
        if docstring:
            code += f'    """{docstring}"""\n'
        else:
            code += f'    """{function_name} function."""\n'

        code += "    pass\n\n"

        # Append to existing content or create new
        if existing_content:
            final_content = existing_content + "\n" + code
        else:
            final_content = f'"""\n{file_path.stem} module.\n"""\n\n' + code

        # Write to file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        # Show relative path for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_path = full_path.relative_to(base_path)
        except ValueError:
            display_path = full_path

        action = "appended to" if existing_content else "created in"
        return f"✅ Successfully {action} function '{function_name}' in {display_path}"

    except Exception as e:
        return f"❌ Error generating Python function: {str(e)}"


def generate_project_structure(project_name: str, project_root: str = None,
                             project_type: str = "python", include_tests: bool = True,
                             include_docs: bool = True) -> str:
    """
    Generate a complete project structure with common files and directories.

    Args:
        project_name: Name of the project
        project_root: Where to create the project
        project_type: Type of project (python, javascript, react, etc.)
        include_tests: Whether to include test directories
        include_docs: Whether to include documentation

    Returns:
        String with generation result
    """
    try:
        base_path = resolve_project_path(project_root or ".", None)
        project_path = base_path / project_name

        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        if project_type.lower() == "python":
            # Python project structure
            dirs = [
                f"{project_name}",
                "tests" if include_tests else None,
                "docs" if include_docs else None,
                "scripts",
                "data"
            ]

            for dir_name in filter(None, dirs):
                dir_path = project_path / dir_name
                dir_path.mkdir(exist_ok=True)

                # Add __init__.py for Python packages
                if dir_name in [project_name, "tests"]:
                    init_file = dir_path / "__init__.py"
                    init_file.write_text(f'"""{dir_name} package."""\n')
                    created_files.append(str(init_file.relative_to(base_path)))

            # Create main module
            main_file = project_path / f"{project_name}" / "main.py"
            main_content = f'''"""
Main module for {project_name}.
"""


def main():
    """Main function."""
    print("Hello from {project_name}!")


if __name__ == "__main__":
    main()
'''
            main_file.write_text(main_content)
            created_files.append(str(main_file.relative_to(base_path)))

            # Create requirements.txt
            req_file = project_path / "requirements.txt"
            req_file.write_text("# Add your dependencies here\n")
            created_files.append(str(req_file.relative_to(base_path)))

            # Create setup.py
            setup_file = project_path / "setup.py"
            setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    description="A Python project",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # Add dependencies here
    ],
    entry_points={{
        "console_scripts": [
            "{project_name}={project_name}.main:main",
        ],
    }},
)
'''
            setup_file.write_text(setup_content)
            created_files.append(str(setup_file.relative_to(base_path)))

        elif project_type.lower() in ["javascript", "js", "node"]:
            # JavaScript/Node.js project structure
            dirs = ["src", "tests" if include_tests else None, "docs" if include_docs else None]

            for dir_name in filter(None, dirs):
                (project_path / dir_name).mkdir(exist_ok=True)

            # Create package.json
            package_file = project_path / "package.json"
            package_content = f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {{
    "start": "node src/index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": [],
  "author": "",
  "license": "ISC"
}}
'''
            package_file.write_text(package_content)
            created_files.append(str(package_file.relative_to(base_path)))

            # Create main file
            main_file = project_path / "src" / "index.js"
            main_content = f'''/**
 * Main module for {project_name}
 */

console.log('Hello from {project_name}!');
'''
            main_file.write_text(main_content)
            created_files.append(str(main_file.relative_to(base_path)))

        # Create common files
        # README.md
        readme_file = project_path / "README.md"
        readme_content = f'''# {project_name}

## Description

A new {project_type} project.

## Installation

```bash
# Add installation instructions here
```

## Usage

```bash
# Add usage instructions here
```

## License

MIT License
'''
        readme_file.write_text(readme_content)
        created_files.append(str(readme_file.relative_to(base_path)))

        # .gitignore
        gitignore_file = project_path / ".gitignore"
        if project_type.lower() == "python":
            gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
        else:
            gitignore_content = '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production
build/
dist/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
'''
        gitignore_file.write_text(gitignore_content)
        created_files.append(str(gitignore_file.relative_to(base_path)))

        result = f"✅ Successfully created {project_type} project '{project_name}'\n\n"
        result += f"📁 Project directory: {project_path.relative_to(base_path)}\n\n"
        result += f"📄 Created files:\n"
        for file_path in created_files:
            result += f"  - {file_path}\n"

        return result

    except Exception as e:
        return f"❌ Error generating project structure: {str(e)}"


def generate_test_file(source_file: str, test_file: str = None, project_root: str = None,
                      test_framework: str = "unittest") -> str:
    """
    Generate a test file template for a source file.

    Args:
        source_file: Path to the source file to test
        test_file: Path for the test file (auto-generated if None)
        project_root: Project root directory
        test_framework: Test framework to use (unittest, pytest)

    Returns:
        String with generation result
    """
    try:
        source_path = resolve_project_path(source_file, project_root)

        if not source_path.exists():
            return f"❌ Source file '{source_path}' does not exist"

        # Auto-generate test file path if not provided
        if test_file is None:
            test_dir = source_path.parent / "tests"
            test_file_name = f"test_{source_path.stem}.py"
            test_path = test_dir / test_file_name
        else:
            test_path = resolve_project_path(test_file, project_root)

        # Create test directory if it doesn't exist
        test_path.parent.mkdir(parents=True, exist_ok=True)

        # Analyze source file to extract functions/classes
        functions, classes = extract_testable_items(source_path)

        # Generate test code based on framework
        if test_framework.lower() == "unittest":
            test_code = generate_unittest_template(source_path, functions, classes, project_root)
        elif test_framework.lower() == "pytest":
            test_code = generate_pytest_template(source_path, functions, classes, project_root)
        else:
            return f"❌ Unsupported test framework: {test_framework}"

        # Write test file
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_code)

        # Show relative paths for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_source = source_path.relative_to(base_path)
            display_test = test_path.relative_to(base_path)
        except ValueError:
            display_source = source_path
            display_test = test_path

        result = f"✅ Successfully generated {test_framework} test file\n"
        result += f"📄 Source: {display_source}\n"
        result += f"🧪 Test: {display_test}\n"
        result += f"📋 Generated {len(functions)} function tests and {len(classes)} class tests"

        return result

    except Exception as e:
        return f"❌ Error generating test file: {str(e)}"


def generate_documentation(file_path: str, doc_file: str = None, project_root: str = None,
                          doc_format: str = "markdown") -> str:
    """
    Generate documentation for a source file.

    Args:
        file_path: Path to the source file
        doc_file: Path for the documentation file
        project_root: Project root directory
        doc_format: Documentation format (markdown, rst)

    Returns:
        String with generation result
    """
    try:
        source_path = resolve_project_path(file_path, project_root)

        if not source_path.exists():
            return f"❌ Source file '{source_path}' does not exist"

        # Auto-generate doc file path if not provided
        if doc_file is None:
            doc_dir = source_path.parent / "docs"
            ext = "md" if doc_format.lower() == "markdown" else "rst"
            doc_file_name = f"{source_path.stem}.{ext}"
            doc_path = doc_dir / doc_file_name
        else:
            doc_path = resolve_project_path(doc_file, project_root)

        # Create docs directory if it doesn't exist
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        # Analyze source file
        functions, classes = extract_testable_items(source_path)

        # Generate documentation
        if doc_format.lower() == "markdown":
            doc_content = generate_markdown_docs(source_path, functions, classes)
        elif doc_format.lower() == "rst":
            doc_content = generate_rst_docs(source_path, functions, classes)
        else:
            return f"❌ Unsupported documentation format: {doc_format}"

        # Write documentation file
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        # Show relative paths for cleaner output
        if project_root:
            base_path = Path(project_root).resolve()
        else:
            base_path = Path.cwd().resolve()

        try:
            display_source = source_path.relative_to(base_path)
            display_doc = doc_path.relative_to(base_path)
        except ValueError:
            display_source = source_path
            display_doc = doc_path

        return f"✅ Successfully generated {doc_format} documentation\n📄 Source: {display_source}\n📚 Docs: {display_doc}"

    except Exception as e:
        return f"❌ Error generating documentation: {str(e)}"


def extract_testable_items(file_path: Path) -> tuple[List[str], List[str]]:
    """Extract functions and classes from a Python file."""
    functions = []
    classes = []

    try:
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

    except Exception:
        pass

    return functions, classes


def generate_unittest_template(source_path: Path, functions: List[str], classes: List[str], project_root: str = None) -> str:
    """Generate unittest template."""
    module_name = source_path.stem

    # Calculate relative import path
    if project_root:
        base_path = Path(project_root).resolve()
        try:
            rel_path = source_path.relative_to(base_path)
            import_path = '.'.join(rel_path.with_suffix('').parts)
        except ValueError:
            import_path = module_name
    else:
        import_path = module_name

    code = f'''"""
Unit tests for {module_name}.
"""

import unittest
from {import_path} import {', '.join(functions + classes) if functions + classes else '*'}


'''

    # Generate test classes for each class
    for class_name in classes:
        code += f'''class Test{class_name}(unittest.TestCase):
    """Test cases for {class_name} class."""

    def setUp(self):
        """Set up test fixtures."""
        self.instance = {class_name}()

    def test_init(self):
        """Test {class_name} initialization."""
        self.assertIsInstance(self.instance, {class_name})

    # TODO: Add more specific tests for {class_name}


'''

    # Generate test class for functions
    if functions:
        code += '''class TestFunctions(unittest.TestCase):
    """Test cases for module functions."""

'''
        for func_name in functions:
            code += f'''    def test_{func_name}(self):
        """Test {func_name} function."""
        # TODO: Implement test for {func_name}
        pass

'''

    code += '''

if __name__ == '__main__':
    unittest.main()
'''

    return code


def generate_pytest_template(source_path: Path, functions: List[str], classes: List[str], project_root: str = None) -> str:
    """Generate pytest template."""
    module_name = source_path.stem

    # Calculate relative import path
    if project_root:
        base_path = Path(project_root).resolve()
        try:
            rel_path = source_path.relative_to(base_path)
            import_path = '.'.join(rel_path.with_suffix('').parts)
        except ValueError:
            import_path = module_name
    else:
        import_path = module_name

    code = f'''"""
Pytest tests for {module_name}.
"""

import pytest
from {import_path} import {', '.join(functions + classes) if functions + classes else '*'}


'''

    # Generate fixtures for classes
    for class_name in classes:
        code += f'''@pytest.fixture
def {class_name.lower()}_instance():
    """Fixture for {class_name} instance."""
    return {class_name}()


'''

    # Generate tests for classes
    for class_name in classes:
        code += f'''class Test{class_name}:
    """Test cases for {class_name} class."""

    def test_init(self, {class_name.lower()}_instance):
        """Test {class_name} initialization."""
        assert isinstance({class_name.lower()}_instance, {class_name})

    # TODO: Add more specific tests for {class_name}


'''

    # Generate tests for functions
    for func_name in functions:
        code += f'''def test_{func_name}():
    """Test {func_name} function."""
    # TODO: Implement test for {func_name}
    pass


'''

    return code


def generate_markdown_docs(source_path: Path, functions: List[str], classes: List[str]) -> str:
    """Generate Markdown documentation."""
    module_name = source_path.stem

    doc = f'''# {module_name}

## Overview

Documentation for the `{module_name}` module.

## Classes

'''

    for class_name in classes:
        doc += f'''### {class_name}

TODO: Add description for {class_name}

#### Methods

- `__init__()`: Constructor
- TODO: Add other methods

'''

    if functions:
        doc += '''## Functions

'''
        for func_name in functions:
            doc += f'''### {func_name}()

TODO: Add description for {func_name}

**Parameters:**
- TODO: Add parameters

**Returns:**
- TODO: Add return description

'''

    doc += f'''## Usage

```python
import {module_name}

# TODO: Add usage examples
```
'''

    return doc


def generate_rst_docs(source_path: Path, functions: List[str], classes: List[str]) -> str:
    """Generate reStructuredText documentation."""
    module_name = source_path.stem

    doc = f'''{module_name}
{'=' * len(module_name)}

Overview
--------

Documentation for the ``{module_name}`` module.

Classes
-------

'''

    for class_name in classes:
        doc += f'''{class_name}
{'^' * len(class_name)}

TODO: Add description for {class_name}

Methods
~~~~~~~

- ``__init__()``: Constructor
- TODO: Add other methods

'''

    if functions:
        doc += '''Functions
---------

'''
        for func_name in functions:
            doc += f'''{func_name}()
{'^' * (len(func_name) + 2)}

TODO: Add description for {func_name}

**Parameters:**

- TODO: Add parameters

**Returns:**

- TODO: Add return description

'''

    doc += f'''Usage
-----

.. code-block:: python

   import {module_name}

   # TODO: Add usage examples
'''

    return doc
