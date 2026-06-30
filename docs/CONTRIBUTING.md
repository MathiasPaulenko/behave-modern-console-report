# Contributing

Contributions are welcome. Please follow the guidelines below to keep the
project consistent and maintainable.

## Development Setup

1. Fork the repository and clone your fork.
2. Create a virtual environment.
3. Install the project in editable mode with development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_models.py
```

## Linting and Formatting

```bash
ruff check .
ruff format .
```

## Type Checking

```bash
mypy behave_modern_console_report
```

## Code Style

- Use Python 3.11+ type hints.
- Prefer dataclasses for data models.
- Write Google-style docstrings.
- Keep formatters thin and place business logic in the Collector and
  Render layers.
- Add tests for new behavior.

## Submitting Changes

1. Create a feature branch.
2. Make your changes with clear, focused commits.
3. Ensure all tests pass and linting is clean.
4. Open a pull request with a description of the change and the motivation.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub
with a clear description and, if possible, steps to reproduce.
