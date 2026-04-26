# --- Project Name ----
NAME        = call_me_maybe

# --- Executables and Paths ---
PYTHON = uv run python

# --- Colors for Terminal ---
GREEN        = \033[0;32m
RED          = \033[0;31m
YELLOW       = \033[0;33m
CYAN         = \033[0;36m
RESET        = \033[0m

# --- Main rules ---
all: install

install:
	@echo "$(CYAN)Installing dependencies with uv...$(RESET)"
	uv sync

run:
	@echo "$(GREEN)Running the project...$(RESET)"
	$(PYTHON) -m src

debug:
	@echo "$(YELLOW)Running in debug mode...$(RESET)"
	$(PYTHON) -m pdb -m src

clean:
	@echo "$(RED)Cleaning caches...$(RESET)"
	rm -rf .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

# --- Linting (Code Quality) ---
lint:
	@echo "$(GREEN)Running flake8...$(RESET)"
	-$(PYTHON) -m flake8 .
	@echo "$(GREEN)Running mypy...$(RESET)"
	-$(PYTHON) -m mypy . \
		--warn-return-any --warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "$(RED)Running flake8...$(RESET)"
	-$(PYTHON) -m flake8 .
	@echo "$(RED)Running mypy --strict...$(RESET)"
	-$(PYTHON) -m mypy . --strict

test:
	@echo "$(GREEN)Running pytest...$(RESET)"
	-$(PYTHON) -m pytest -v

.PHONY: all install run debug clean lint lint-strict test
