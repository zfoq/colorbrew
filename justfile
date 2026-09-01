default:
    @just --list

sync:
    uv sync

test:
    uv run pytest -q

coverage:
    uv run pytest --cov=src/colorbrew --cov-report=term-missing -q

lint:
    uv run ruff check .

format:
    uv run ruff format .
