.PHONY: install run debug clean lint lint-strict test help

PYTHON := python3
VENV_DIR := venv
MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

help:
	@echo "Pac-Man Makefile targets:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run game"
	@echo "  make debug        - Run with pdb debugger"
	@echo "  make clean        - Remove cache and temp files"
	@echo "  make lint         - Run flake8 and mypy"
	@echo "  make lint-strict  - Run flake8 and mypy with strict flags"
	@echo "  make test         - Run pytest"

install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install --user mazegenerator-2.0.2-py3-none-any.whl
	$(PYTHON) -m pip install --user -r requirements.txt

run:
	@echo "Running Pac-Man..."
	@$(PYTHON) pac-man.py config.json

debug:
	@echo "Running Pac-Man in debug mode..."
	@$(PYTHON) -m pdb pac-man.py config.json

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

lint:
	@echo "Running flake8..."
	flake8 .
	@echo "Running mypy..."
	mypy pacman tests $(MYPY_FLAGS)

lint-strict:
	@echo "Running flake8..."
	flake8 .
	@echo "Running mypy (strict)..."
	mypy pacman tests --strict

test:
	@echo "Running pytest..."
	SDL_VIDEODRIVER=dummy pytest tests/ -v
