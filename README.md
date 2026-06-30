# Behave Modern Console Report

[![PyPI](https://img.shields.io/badge/pypi-behave--modern--console--report-blue)](https://pypi.org/p/behave-modern-console-report)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A modern console report formatter for [Behave](https://github.com/behave/behave) that provides rich terminal output with colors, progress indicators, execution summaries, timings, and failure diagnostics.

Inspired by modern developer tools such as Playwright CLI, pytest, and Cargo.

## Table of Contents

- [Formatters](#formatters)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Example output](#example-output)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Development](#development)
- [Changelog](#changelog)
- [License](#license)

## Formatters

| Formatter | Description |
| --- | --- |
| `modern` | Playwright-like report with feature grouping, scenario/step lines, and end-of-run summary. |
| `modern-live` | Live-updating version of `modern` using Rich Live for real-time status colors. |
| `progress` | Single-line live progress bar that updates in place. |
| `log` | Timestamped log output for every completed scenario and step. |
| `ci` | CI-friendly output with colored status tags and end-of-run failure summary. |
| `minimal` | Plain text output with only scenario names and a final summary. |

## Installation

Install from PyPI:

```bash
pip install behave-modern-console-report
```

Or install from source:

```bash
git clone https://github.com/MathiasPaulenko/behave-modern-console-report.git
cd behave-modern-console-report
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick start

1. Create or update `behave.ini` in your Behave project root:

```ini
[behave]
default_format=modern

[behave.formatters]
modern = behave_modern_console_report.formatters.modern:ModernFormatter
```

2. Run Behave:

```bash
behave
```

You can also select a formatter from the command line:

```bash
behave --format=modern-live
```

Or use the full module path without registering:

```bash
behave -f behave_modern_console_report.formatters.modern:ModernFormatter
```

## Configuration

All options are passed through Behave's `userdata` mechanism. Add a `[behave.userdata]` section to `behave.ini`:

```ini
[behave.userdata]
mcr.colors = true
mcr.show_steps = true
mcr.show_traceback = true
```

Each formatter reads its own `mcr.<formatter>.<key>` namespace with fallback to global `mcr.<key>` keys. The `show_progress` option is formatter-specific (no global fallback).

| Option | Default | Description |
| --- | --- | --- |
| `mcr.colors` | `true` | Enable/disable colored output. |
| `mcr.show_steps` | `true` | Show step-level details. |
| `mcr.show_traceback` | `true` | Show tracebacks for failed steps. |
| `mcr.<formatter>.show_progress` | `true` | Show progress bar (formatter-specific, no global fallback). |

Override from the command line:

```bash
behave --format=modern -D mcr.colors=false -D mcr.show_steps=false
```

See [docs/configuration.md](docs/configuration.md) for the full reference.

## Example output

```text
🚀 Behave Modern Console Report

Feature: Authentication

  ✓ Login  (602ms)
  ✗ Locked account shows error  (604ms)
  ⏭ Login with social provider  (0ms)

RESULTS

  Passed   18
  Failed   1
  Skipped  1

  ⏱ Duration 9.1s
```

## Architecture

```text
Behave → BaseFormatter → Collector → Models → Render → Console
```

| Layer | File | Responsibility |
| ----- | ---- | -------------- |
| BaseFormatter | `base.py` | Receives Behave events and forwards them to the Collector. |
| Collector | `collector.py` | Builds the `Execution` model from Behave objects. |
| Models | `models.py` | Pure dataclasses for Execution, Feature, Scenario, Step, and Error. |
| Render | `render.py` | Converts the model into Rich `Text` objects for terminal output. |
| Formatters | `formatters/` | Each formatter renders the model differently. |
| Config | `config.py` | Resolves per-formatter and global settings from Behave user data. |

See [docs/architecture.md](docs/architecture.md) for details.

## Documentation

- [docs/configuration.md](docs/configuration.md) — all `mcr.*` options and per-formatter overrides.
- [docs/usage.md](docs/usage.md) — usage examples and combining formatters.
- [docs/ci-cd.md](docs/ci-cd.md) — GitHub Actions, GitLab CI, Azure DevOps, and Jenkins examples.
- [docs/architecture.md](docs/architecture.md) — layered architecture and data flow.
- [docs/contributing.md](docs/contributing.md) — development setup, code style, and submitting changes.

## Development

```bash
pytest
ruff check .
mypy behave_modern_console_report
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT
