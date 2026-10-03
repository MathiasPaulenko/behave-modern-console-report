# Behave Modern Console Report

[![PyPI](https://img.shields.io/badge/pypi-behave--modern--console--report-blue)](https://pypi.org/p/behave-modern-console-report)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A modern console report formatter for [Behave](https://github.com/behave/behave) that provides rich terminal output with colors, progress indicators, execution summaries, timings, and failure diagnostics.

Inspired by modern developer tools such as Playwright CLI, pytest, and Cargo.

## Table of Contents

- [Features](#features)
- [Formatters](#formatters)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Example output](#example-output)
- [CI/CD](#cicd)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Development](#development)
- [Changelog](#changelog)
- [License](#license)

## Features

- **Six formatters**: `modern-console`, `modern-console-live`, `progress`, `log`, `ci`, and `minimal` — each designed for a different use case.
- **Real-time output**: Live scenario status updates as tests execute.
- **Progress bar**: Completion percentage and scenario count during execution.
- **Colored status icons**: Unicode icons (✓ ✗ ⏭ ? P ◌) with color-coded results via Rich.
- **Failure diagnostics**: Scenario name, error type, short message, and optional traceback.
- **Per-formatter configuration**: `mcr.<formatter>.<key>` with global `mcr.<key>` fallback.
- **CI-friendly**: The `ci` formatter produces compact, log-friendly output with colored status tags.
- **Lightweight**: Only `rich` as an external dependency (besides `behave`).
- **Cross-platform**: Works on Windows, macOS, and Linux. Output is always UTF-8-safe, so Unicode icons never crash on non-UTF-8 terminals or when redirected to a file.

## Formatters

| Formatter | Description | Best for |
| --- | --- | --- |
| `modern-console` | Playwright-like report with feature grouping, scenario/step lines, and end-of-run summary. | Local development. |
| `modern-console-live` | Live-updating version of `modern-console` using Rich Live for real-time status colors. | Interactive terminals. |
| `progress` | Single-line live progress bar that updates in place. | Quick runs, overview. |
| `log` | Timestamped log output for every completed scenario and step. | CI logs, debugging. |
| `ci` | CI-friendly output with colored status tags and end-of-run failure summary. | CI/CD pipelines. |
| `minimal` | Plain text output with only scenario names and a final summary. | Minimal noise, piping. |

### Formatter examples

**`modern-console`** — grouped by feature with steps:

```text
🚀 Behave Modern Console Report
Running scenarios...


Feature: Authentication

  ✓ Login  (602ms)
    ✓ Given I am on the login page
    ✓ When I enter valid credentials  (602ms)
    ✓ Then I should be logged in
  ✗ Locked account shows error  (604ms)
    ✓ Given I am on the login page
    ✓ When I enter credentials for a locked account  (604ms)
    ✗ Then I should see an error message
      Invalid credentials
  ⏭ Login with social provider
    ⏭ Given I am on the login page
    ⏭ When I choose to login with OAuth
    ⏭ Then I should be logged in

RESULTS

  Passed   18
  Failed   1
  Skipped  1

  ⏱ Duration 9.1s

Failures

✗ Locked account shows error
  Feature: Authentication, scenario at line 25
  AssertionError
  Invalid credentials
  ASSERT FAILED: Invalid credentials
```

**`progress`** — single-line live update:

```text
████████████████████ 100% 20/20 - done
```

**`log`** — timestamped lines:

```text
[2026-06-30 12:00:01] [PASSED] Scenario passed: Login (602ms)
[2026-06-30 12:00:02] [FAILED] Scenario failed: Locked account shows error (604ms)
[2026-06-30 12:00:02] [SKIPPED] Scenario skipped: Login with social provider (0ms)
```

**`ci`** — colored status tags (with `Feature / Scenario` context):

```text
[PASSED] Authentication / Login (602ms)
[FAILED] Authentication / Locked account shows error (604ms)
[SKIPPED] Authentication / Login with social provider (0ms)

████████████████████ 100% 20/20 scenarios

RESULTS

  Passed   18
  Failed   1
  Skipped  1

  ⏱ Duration 9.1s
```

**`minimal`** — plain text only:

```text
[PASSED] Login (602ms)
[FAILED] Locked account shows error (604ms)
[SKIPPED] Login with social provider (0ms)
RESULTS
  Passed 18
  Failed 1
  Skipped 1
  Duration 9.1s
```

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
default_format=modern-console

[behave.formatters]
modern-console = behave_modern_console_report.formatters.modern:ModernFormatter
modern-console-live = behave_modern_console_report.formatters.modern_live:ModernLiveFormatter
progress = behave_modern_console_report.formatters.progress:ProgressFormatter
log = behave_modern_console_report.formatters.log:LogFormatter
ci = behave_modern_console_report.formatters.ci:CIFormatter
minimal = behave_modern_console_report.formatters.minimal:MinimalFormatter
```

1. Run Behave:

```bash
behave
```

You can also select a formatter from the command line:

```bash
behave --format=modern-console-live
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

Each formatter reads its own `mcr.<formatter>.<key>` namespace with fallback to global `mcr.<key>` keys. `<formatter>` is the registered formatter name: `modern-console`, `modern-console-live`, `progress`, `log`, `ci`, or `minimal`. The `show_progress` option is formatter-specific (no global fallback).

| Option | Default | Description |
| --- | --- | --- |
| `mcr.colors` | `true` | Enable/disable colored output. Colors are also auto-disabled when output is not a terminal (pipes, `-o` files). |
| `mcr.show_steps` | `true` | Show step-level details. |
| `mcr.show_traceback` | `true` | Show tracebacks for failed steps. |
| `mcr.<formatter>.show_progress` | `true` | Show progress bar (formatter-specific, no global fallback). |

Override from the command line:

```bash
behave --format=modern-console -D mcr.colors=false -D mcr.show_steps=false
```

See [docs/configuration.md](docs/configuration.md) for the full reference.

## Example output

```text
🚀 Behave Modern Console Report
Running scenarios...


Feature: Authentication

  ✓ Login  (602ms)
  ✗ Locked account shows error  (604ms)
  ⏭ Login with social provider

RESULTS

  Passed   18
  Failed   1
  Skipped  1

  ⏱ Duration 9.1s
```

## CI/CD

The `ci` formatter is designed for CI pipelines — compact, colored status tags, and a final failure summary.

```bash
behave --format=ci -D mcr.colors=false
```

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: behave --format=ci -D mcr.colors=false
```

### Combining with the Markdown report

Show console output and generate a Markdown report at the same time:

```bash
behave -f ci -o /dev/null -f behave_modern_md_report.formatter:BehaveMarkdownFormatter -o report.md
```

On Windows use `NUL` instead of `/dev/null`. You can also send the console report to a file with `-o report.txt` — files are written in UTF-8 without ANSI codes.

See [docs/ci-cd.md](docs/ci-cd.md) for GitLab CI, Azure DevOps, and Jenkins examples.

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
- [CONTRIBUTING.md](CONTRIBUTING.md) — development setup, code style, and submitting changes.

The docs are also available as an MkDocs site. To build or serve them locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

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
