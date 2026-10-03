# Behave Modern Console Report

A modern console report formatter for [Behave](https://github.com/behave/behave) that provides rich terminal output with colors, progress indicators, execution summaries, timings, and failure diagnostics.

## Installation

```bash
pip install behave-modern-console-report
```

## Quick start

Register the formatters in your `behave.ini`:

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

Then run `behave` as usual, or select a formatter from the command line:

```bash
behave --format=modern-console-live
```

## Formatters

| Formatter | Best for |
| --- | --- |
| `modern-console` | Local development — Playwright-like report grouped by feature. |
| `modern-console-live` | Interactive terminals — live-updating report via Rich Live. |
| `progress` | Quick runs — single-line live progress bar. |
| `log` | CI logs and debugging — timestamped lines. |
| `ci` | CI/CD pipelines — compact output with status tags. |
| `minimal` | Minimal noise — scenario names and a final summary. |

## Where to next

- [Usage](usage.md) — selecting formatters, combining reports.
- [Configuration](configuration.md) — all `mcr.*` options and per-formatter overrides.
- [CI/CD](ci-cd.md) — GitHub Actions, GitLab CI, Azure DevOps, and Jenkins examples.
- [Architecture](architecture.md) — layered design and data flow.
- [Contributing](contributing.md) — development setup and submitting changes.
