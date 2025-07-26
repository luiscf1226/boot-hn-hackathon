#!/usr/bin/env python3
"""
Setup script for AI Coding Agent package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "AI Coding Agent - A Python-based application for code analysis and assistance"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "sqlalchemy>=2.0.23",
        "google-generativeai>=0.3.2",
        "textual>=0.45.1",
        "rich>=13.7.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ]

setup(
    name="ai-coding-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered coding assistant with terminal UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-coding-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black",
            "flake8",
            "mypy",
        ],
        "build": [
            "pyinstaller>=5.0",
            "build",
            "twine",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-coding-agent=main:main",
            "aca=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": [
            "commands/prompts/*.txt",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-coding-agent/issues",
        "Source": "https://github.com/yourusername/ai-coding-agent",
    },
    keywords="ai coding assistant terminal ui code analysis",
    zip_safe=False,
)