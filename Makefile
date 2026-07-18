.PHONY: bootstrap validate strict lint format format-check type test check clean

bootstrap:
	python3 scripts/bootstrap.py

validate:
	python3 scripts/validate_repo.py

strict:
	python3 scripts/validate_repo.py --strict

lint:
	python3 -m ruff check .

format:
	python3 -m ruff format .

format-check:
	python3 -m ruff format --check .

type:
	python3 -m mypy scripts

test:
	python3 -m pytest

check: validate lint format-check type test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
