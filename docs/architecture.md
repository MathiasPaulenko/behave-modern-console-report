# Architecture

`behave-modern-console-report` follows a clean layered architecture so that
each responsibility is isolated and the project can be extended without
coupling to Behave internals.

## Layers

```text
Behave → Formatter → Collector → Models → Renderer → Console
```

### Formatter (`formatter.py`)

The only layer that implements the Behave `Formatter` API. It forwards events
such as `feature`, `scenario`, `step`, `match`, and `result` to the Collector.
It also decides whether to render output inside a Rich `Live` view or as
log-friendly incremental lines for CI environments.

### Collector (`collector.py`)

Translates Behave model objects into internal dataclasses. It maintains the
current feature, scenario, and step so that partial results can be rendered in
real time. It also updates aggregate counters and captures error information.

### Models (`models.py`)

Pure dataclasses representing the execution state:

- `Execution`
- `Feature`
- `Scenario`
- `Step`
- `Error`
- `Environment`

These classes are independent of Behave and are used by the Renderer.

### Renderer (`renderer.py`)

Converts the execution model into Rich renderables. It produces:

- Header with scenario count
- Progress bar with ETA
- Scenario list
- Results summary
- Failure diagnostics

The Renderer is independent of Behave and can be tested with fake models.

### Console (`console.py`)

Wraps a Rich `Console` configured according to the formatter settings. This
layer abstracts the terminal stream and color settings.

### Configuration (`config.py`)

Resolves settings from Behave user data and environment variables. It also
detects CI environments and adjusts defaults for log-friendly output.

### Themes (`themes.py`) and supporting modules

Themes define semantic styles. `colors.py`, `icons.py`, `progress.py`, and
`statistics.py` provide small, focused helpers used by the Renderer.

## Extensibility

The architecture is designed to support future features such as:

- Interactive TUI mode: replace the Renderer with a Textual-based UI.
- Split panel live view: extend the Renderer with panel layouts.
- Parallel execution visualization: update the Collector to track parallel
  workers and the Renderer to display them.
- Historical comparisons: add a new layer that compares current execution
  models with stored reports.
- Export formats: add exporters that consume the same `Execution` model and
  write JSON, Markdown, or HTML without touching Behave or rendering logic.
- Plugin system: expose hooks in the Collector and Renderer so that third-party
  plugins can transform output.
