# Configuration

Configuration is provided via Behave user data (`-D key=value`) or the `[behave.userdata]` section in `behave.ini`.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `mcr.colors` | `true` | Enable/disable colored output. |
| `mcr.show_steps` | `true` | Show step-level details. |
| `mcr.show_traceback` | `true` | Show tracebacks for failed steps. |
| `mcr.<formatter>.show_progress` | `true` | Show progress bar (formatter-specific, no global fallback). |

## Per-formatter overrides

Each formatter reads its own `mcr.<formatter>.<key>` namespace. When a formatter-specific key is missing, the global `mcr.<key>` is used as a fallback.

The `show_progress` option is formatter-specific only (no global fallback).

## Examples

Disable colors globally:

```bash
behave --format=modern -D mcr.colors=false
```

Override `show_steps` for a specific formatter:

```bash
behave --format=ci -D mcr.ci.show_steps=false -D mcr.show_steps=true
```

Hide progress bar for the CI formatter:

```bash
behave --format=ci -D mcr.ci.show_progress=false
```
