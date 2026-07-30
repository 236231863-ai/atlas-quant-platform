.PHONY: install lint format typecheck test clean

install:
	poetry install --all-groups

lint:
	poetry run ruff check .
	poetry run ruff format --check .

format:
	poetry run ruff format .
	poetry run ruff check --fix .

typecheck:
	poetry run mypy core/ engine/ plugins/

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=core --cov=engine --cov=plugins --cov-report=term

clean:
	rm -rf dist/ build/
	rm -rf .coverage htmlcov/
	rm -rf .mypy_cache .ruff_cache
