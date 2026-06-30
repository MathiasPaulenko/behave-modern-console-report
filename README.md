# behave-modern-console-report

A modern console report formatter for [Behave](https://behave.readthedocs.io/) that provides rich terminal output with colors, progress indicators, execution summaries, timings, and failure diagnostics.

Inspired by modern developer tools such as Playwright CLI, pytest, and Cargo.

---

## Formatters

| Formatter | Description |
| --- | --- |
| `modern` | Playwright-like report with feature grouping, scenario/step lines, and end-of-run summary. |
| `modern-live` | Live-updating version of `modern` using Rich Live for real-time status colors. |
| `progress` | Single-line live progress bar that updates in place. |
| `log` | Timestamped log output for every completed scenario and step. |
| `ci` | CI-friendly output with colored status tags and end-of-run failure summary. |
| `minimal` | Plain text output with only scenario names and a final summary. |

---

## Installation

```bash
pip install behave-modern-console-report
```

For development:

```bash
git clone https://github.com/MathiasPaulenko/behave-modern-console-report.git
cd behave-modern-console-report
pip install -e ".[dev]"
```

---

## Usage

Register the formatter with Behave using the `--format` or `-f` option:

```bash
behave --format=modern
```

Or set it in `behave.ini`:

```ini
[behave]
default_format=modern
```

Disable colors:

```bash
behave --format=modern -D mcr.colors=false
```

Hide step details:

```bash
behave --format=modern -D mcr.show_steps=false
```

---

## Configuration

Options are read from Behave user data (`-D key=value`) or `behave.ini` `[behave.userdata]` section.

Each formatter reads its own `mcr.<formatter>.<key>` namespace with fallback to global `mcr.<key>` keys. The `show_progress` option is formatter-specific (no global fallback).

| Option | Default | Description |
| --- | --- | --- |
| `mcr.colors` | `true` | Enable/disable colored output. |
| `mcr.show_steps` | `true` | Show step-level details. |
| `mcr.show_traceback` | `true` | Show tracebacks for failed steps. |
| `mcr.<formatter>.show_progress` | `true` | Show progress bar (formatter-specific, no global fallback). |

---

## Example Output

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

---

## Architecture

```text
Behave → BaseFormatter → Collector → Models → Render → Console
```

- **BaseFormatter**: Receives Behave events and forwards them to the Collector.
- **Collector**: Builds an internal execution model from Behave events.
- **Models**: Dataclasses for Execution, Feature, Scenario, Step, and Error.
- **Render**: Converts the model into Rich Text objects for terminal output.
- **Formatters**: Each formatter renders the model differently (live, log, CI, etc.).

---

## Development

```bash
pytest
ruff check .
mypy behave_modern_console_report
```

---

## License

MIT
