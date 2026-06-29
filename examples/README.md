# Behave Examples

This directory contains runnable Behave examples that demonstrate the modern
console report formatter.

## Running the Examples

Make sure you have installed the package in editable mode:

```bash
cd ..
pip install -e ".[dev]"
```

Then run the examples from this directory:

```bash
behave
```

The `behave.ini` file already configures the `modern` formatter.

## What You Will See

The example feature includes:

- **Successful login** - a passing scenario.
- **Failed login** - a passing scenario that validates error handling.
- **Login with social provider** - a scenario skipped via the `@skip` tag.
- **Locked account shows error** - a scenario that fails intentionally to show
  failure diagnostics in the console.

## Run with Options

Try different verbosity levels:

```bash
behave -D modern_console_verbosity=verbose
behave -D modern_console_verbosity=minimal
```

Try different themes:

```bash
behave -D modern_console_theme=dark
behave -D modern_console_theme=light
behave -D modern_console_theme=monochrome
```

Disable colors (useful for CI or piping to a file):

```bash
behave -D modern_console_colors=false
```

## Using the Helper Script

On Windows, you can also run the helper script:

```bash
python run_examples.py
```

This script runs `behave` with the modern formatter and prints the captured
output to the console.
