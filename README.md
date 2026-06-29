# behave-modern-console-report

A modern, real-time console report formatter for [Behave](https://behave.readthedocs.io/) that provides rich terminal output with colors, progress indicators, execution summaries, timings, and developer-friendly diagnostics for local development and CI/CD pipelines.

Inspired by modern developer tools such as Playwright CLI, pytest, Cargo, and GitHub CLI.

---

## Features

- **Real-time output**: Live scenario status updates as tests execute.
- **Beautiful progress bar**: Current scenario, percentage completed, and estimated remaining time.
- **Clear pass/fail feedback**: Unicode icons and color-coded results.
- **Failure diagnostics**: Scenario name, error type, short message, and optional traceback.
- **Verbosity levels**: minimal, normal, verbose, and debug.
- **Multiple themes**: default, dark, light, minimal, and monochrome.
- **CI/CD friendly**: Automatically detects CI environments and disables animations.
- **Lightweight and fast**: Handles thousands of scenarios and steps efficiently.
- **Extensible architecture**: Designed for future TUI, plugins, and export formats.

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

Specify verbosity with Behave user data:

```bash
behave --format=modern -D mcr.verbosity=verbose
```

Choose a theme:

```bash
behave --format=modern -D mcr.theme=dark
```

Disable colors (useful for CI):

```bash
behave --format=modern -D mcr.colors=false
```

Run in compact mode:

```bash
behave --format=modern -D mcr.compact=true
```

---

## Example Output

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Behave Modern Console Report

Running 128 scenarios...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Login
✓ Register
✗ Checkout
✓ Search
⏭ Payments

███████████████░░░░░░░░  72%
106 / 148 scenarios

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESULTS

Passed   148
Failed   2
Skipped  4

Duration 3m42s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Failed scenarios are shown with concise diagnostics:

```text
✗ Checkout scenario

AssertionError:
Expected 200
Actual 500
```

---

## Configuration Reference

Options are read from Behave user data (`-D key=value`) or environment variables.

| Option | Environment Variable | Default | Description |
| --- | --- | --- | --- |
| `mcr.theme` | `MCR_THEME` | `default` | Output theme. |
| `mcr.verbosity` | `MCR_VERBOSITY` | `normal` | Output verbosity. |
| `mcr.colors` | `MCR_COLORS` | `auto` | Enable/disable colors. |
| `mcr.compact` | `MCR_COMPACT` | `false` | Compact output mode. |
| `mcr.show_steps` | `MCR_SHOW_STEPS` | `auto` | Show step-level details. |
| `mcr.show_durations` | `MCR_SHOW_DURATIONS` | `true` | Show scenario durations. |
| `mcr.show_progress` | `MCR_SHOW_PROGRESS` | `true` | Show progress bar. |
| `mcr.show_traceback` | `MCR_SHOW_TRACEBACK` | `true` | Show tracebacks on failure. |
| `mcr.live` | `MCR_LIVE` | `auto` | Force live/interactive mode. |

The legacy `modern_console_*` keys are still supported for backwards compatibility.

---

## Architecture

```text
Behave → Formatter → Collector → Model → Renderer → Console Output
```

- **Formatter**: Thin entry point that receives Behave events.
- **Collector**: Builds an internal execution model from events.
- **Models**: Dataclasses representing execution, features, scenarios, steps, and errors.
- **Renderer**: Converts the model into terminal output independently of Behave.
- **Console**: Manages the terminal output stream, including live updates.

This layered design makes it easy to extend the formatter with new output modes, themes, or export formats in the future.

---

## Development

Run the test suite:

```bash
pytest
```

Run linting:

```bash
ruff check .
ruff format .
```

Run type checking:

```bash
mypy behave_modern_console_report
```

---

## Contributing

Contributions are welcome. Please open an issue or pull request on GitHub. For major changes, please discuss them in an issue first.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
