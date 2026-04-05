# Makefile for common developer tasks

POETRY := poetry

.PHONY: help install-dev pre-commit-install test format lint typecheck

help:
	@echo "Makefile targets:"
	@echo "  install-dev        Install development dependencies (Poetry)"
	@echo "  pre-commit-install Install pre-commit hooks"
	@echo "  test               Run tests (pytest)"
	@echo "  format             Run code formatters (isort, black)"
	@echo "  lint               Check formatting and run type checks"
	@echo "  typecheck          Run mypy type checks"

install-dev:
	@echo "Installing development dependencies..."
	@$(POETRY) install --with dev || $(POETRY) install

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@$(POETRY) run pre-commit install --install-hooks

test:
	@$(POETRY) run pytest -q

format:
	@$(POETRY) run isort --profile black .
	@$(POETRY) run black .

lint:
	@$(POETRY) run isort --profile black --check-only .
	@$(POETRY) run black --check .
	@$(POETRY) run python -m mypy .

typecheck:
	@$(POETRY) run python -m mypy .
