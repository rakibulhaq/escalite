# Development

This project uses Poetry to manage dependencies and provides a Makefile with common developer tasks.

Prerequisites
- Poetry installed (https://python-poetry.org/)

Install development dependencies

```bash
# Install all dependencies including dev group (Poetry 1.2+)
poetry install --with dev

# If your Poetry is older, run:
poetry install
# or add dev tools manually:
poetry add --group dev black isort mypy pre-commit pytest
```

Install pre-commit hooks

```bash
make pre-commit-install
# or
poetry run pre-commit install --install-hooks
```

Common Makefile targets

- `make test` — run tests with pytest
- `make format` — run `isort` then `black` to format code
- `make lint` — check formatting and run mypy type checks
- `make typecheck` — run `mypy` type checking
- `make install-dev` — install development dependencies

Examples

Run all tests:

```bash
make test
```

Format the codebase:

```bash
make format
```

Check formatting and types:

```bash
make lint
make typecheck
```

Run a single test:

```bash
poetry run pytest tests/path/to/test_file.py::test_name -q
```

Run a specific pre-commit hook on all files:

```bash
poetry run pre-commit run black --all-files
```

Troubleshooting

- To update pinned pre-commit hooks:

```bash
poetry run pre-commit autoupdate
```

- If `pre-commit` is not installed, ensure dev dependencies are present via `poetry install --with dev`.

Configurations
- Formatting and type-checking are governed by `pyproject.toml` (black/isort/mypy) and `.pre-commit-config.yaml` for git hooks.
