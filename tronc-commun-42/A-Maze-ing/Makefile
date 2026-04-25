.PHONY: install run debug clean lint lint-strict build

install:
	pip install -r requirements.txt

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache mazegen/__pycache__ dist build *.egg-info mazegen/*.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	python3 -m build
	cp dist/mazegen-1.0.0-py3-none-any.whl . 2>/dev/null || true
	cp dist/mazegen-1.0.0.tar.gz . 2>/dev/null || true
