.PHONY: install test lint format build

install:
	poetry install

test:
	poetry run pytest --cov

lint:
	poetry run black --check escalite tests

format:
	poetry run black escalite tests

build:
	poetry build
