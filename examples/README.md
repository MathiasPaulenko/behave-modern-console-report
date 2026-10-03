# Behave Examples

This directory contains runnable Behave examples that demonstrate the modern
console report formatters.

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

The `behave.ini` file registers all six formatters and selects `progress` as
the default. Pick another one from the command line:

```bash
behave --format=modern-console
behave --format=modern-console-live
behave --format=ci
behave --format=log
behave --format=minimal
```

## What You Will See

The example features exercise all outcome types:

- **User Login** — passing scenarios, a scenario skipped via the `@skip` tag,
  and "Locked account shows error", which fails intentionally to demonstrate
  failure diagnostics.
- **Shopping Cart** and **Checkout** — regular passing scenarios tagged
  `@smoke` and `@regression`.
- **Product Catalog** — a `Scenario Outline` (reported as one scenario per
  example row) and filter/search scenarios.

## Configuration Options

Formatters are configured through Behave `userdata` (`-D` or
`[behave.userdata]` in `behave.ini`):

```bash
# Disable colors (useful for CI or piping to a file)
behave -D mcr.colors=false

# Hide step details and tracebacks
behave -D mcr.show_steps=false -D mcr.show_traceback=false

# Per-formatter override (only affects the ci formatter)
behave --format=ci -D mcr.ci.show_steps=false
```

See [../docs/configuration.md](../docs/configuration.md) for the full option
reference.

## Writing output to a file

```bash
behave --format=modern-console -o report.txt
```

The file is written in UTF-8 without ANSI color codes. On Windows use `NUL`
instead of `/dev/null` when discarding output.

## Using the Helper Script

On Windows, you can also run the helper script:

```bash
python run_examples.py
```

It runs `python -m behave` inside the examples directory and forwards any
extra arguments, so `python run_examples.py --format=ci` works too.
