# Makefile for AI Coding Agent

# Variables
PYTHON := python3
PIP := pip
PACKAGE_NAME := ai-coding-agent
VENV_DIR := venv

# Default target
.PHONY: help
help:
	@echo "AI Coding Agent Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  install-dev     Install development dependencies"
	@echo "  install         Install package in development mode"
	@echo "  build-wheel     Build wheel package for PyPI"
	@echo "  build-sdist     Build source distribution"
	@echo "  build-binary    Build standalone binary executable"
	@echo "  test            Run tests"
	@echo "  lint            Run code linting"
	@echo "  format          Format code with black"
	@echo "  clean           Clean build artifacts"
	@echo "  clean-all       Clean everything including venv"
	@echo "  publish-test    Upload to TestPyPI"
	@echo "  publish         Upload to PyPI"
	@echo "  venv            Create virtual environment"
	@echo ""

# Development setup
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created. Activate with:"
	@echo "source $(VENV_DIR)/bin/activate  # Linux/macOS"
	@echo "$(VENV_DIR)\\Scripts\\activate     # Windows"

.PHONY: install-dev
install-dev:
	$(PIP) install -e ".[dev,build]"

.PHONY: install
install:
	$(PIP) install -e .

# Building
.PHONY: build-wheel
build-wheel:
	$(PYTHON) -m build --wheel

.PHONY: build-sdist
build-sdist:
	$(PYTHON) -m build --sdist

.PHONY: build-all
build-all: build-wheel build-sdist

.PHONY: build-binary
build-binary:
	$(PYTHON) build_binary.py

# Testing and quality
.PHONY: test
test:
	$(PYTHON) -m pytest

.PHONY: lint
lint:
	$(PYTHON) -m flake8 app/ main.py
	$(PYTHON) -m mypy app/ main.py

.PHONY: format
format:
	$(PYTHON) -m black app/ main.py

# Cleaning
.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.spec" -delete

.PHONY: clean-all
clean-all: clean
	rm -rf $(VENV_DIR)/

# Publishing
.PHONY: publish-test
publish-test: build-all
	$(PYTHON) -m twine upload --repository testpypi dist/*

.PHONY: publish
publish: build-all
	$(PYTHON) -m twine upload dist/*

# Install from different sources
.PHONY: install-from-pypi
install-from-pypi:
	$(PIP) install $(PACKAGE_NAME)

.PHONY: install-from-test-pypi
install-from-test-pypi:
	$(PIP) install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)

# Check package
.PHONY: check
check:
	$(PYTHON) -m build --check
	$(PYTHON) -m twine check dist/*

# Run the application
.PHONY: run
run:
	$(PYTHON) main.py

.PHONY: run-installed
run-installed:
	ai-coding-agent