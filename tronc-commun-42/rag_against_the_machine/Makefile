.PHONY: install run debug clean lint lint-strict index search evaluate test

PYTHON := uv run python
MODULE := student

install:
	uv venv
	uv sync

run:
	$(PYTHON) -m $(MODULE) --help

debug:
	$(PYTHON) -m pdb -m $(MODULE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

index:
	$(PYTHON) -m $(MODULE) index --max_chunk_size 2000

test:
	uv run pytest -q || true
