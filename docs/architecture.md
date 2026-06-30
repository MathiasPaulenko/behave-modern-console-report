# Architecture

`behave-modern-console-report` follows a layered architecture so that each responsibility is isolated and the project can be extended without coupling to Behave internals.

## Layers

```text
Behave → BaseFormatter → Collector → Models → Render → Console
```

### BaseFormatter (`base.py`)

Implements the Behave `Formatter` API. It forwards events (`feature`, `scenario`, `step`, `match`, `result`) to the Collector and provides `on_result`/`on_close` hooks for subclasses.

### Collector (`collector.py`)

Translates Behave model objects into internal dataclasses. It maintains the current feature, scenario, and step so that partial results can be rendered in real time. It also updates aggregate counters and captures error information.

### Models (`models.py`)

Pure dataclasses representing the execution state:

- `Execution`
- `Feature`
- `Scenario`
- `Step`
- `Error`

These classes are independent of Behave and can be tested without running Behave.

### Render (`render.py`)

Converts the execution model into Rich `Text` objects. It produces scenario lines, step lines, progress bars, summary blocks, and failure diagnostics.

### Formatters (`formatters/`)

Each formatter renders the model differently:

- `modern` — Playwright-like report with feature grouping.
- `modern-live` — Live-updating report using Rich `Live`.
- `progress` — Single-line live progress bar.
- `log` — Timestamped log output.
- `ci` — CI-friendly output with colored status tags.
- `minimal` — Plain text with only scenarios and summary.

### Configuration (`config.py`)

Resolves settings from Behave user data. Each formatter reads `mcr.<formatter>.<key>` with fallback to global `mcr.<key>` keys. The `show_progress` option is formatter-specific (no global fallback).

## Extensibility

The architecture supports adding new formatters by subclassing `BaseFormatter` and implementing `on_result` and `on_close`. The Collector, Models, and Render layers are shared across all formatters.
