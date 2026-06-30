# Usage

## Installation

```bash
pip install behave-modern-console-report
```

## Basic configuration

Register the formatter in your `behave.ini`:

```ini
[behave]
default_format=modern

[behave.formatters]
modern = behave_modern_console_report.formatters.modern:ModernFormatter
modern-live = behave_modern_console_report.formatters.modern_live:ModernLiveFormatter
log = behave_modern_console_report.formatters.log:LogFormatter
ci = behave_modern_console_report.formatters.ci:CIFormatter
minimal = behave_modern_console_report.formatters.minimal:MinimalFormatter
progress = behave_modern_console_report.formatters.progress:ProgressFormatter
```

Then run Behave as usual:

```bash
behave
```

## Selecting a formatter from the command line

```bash
behave --format=modern-live
```

## Using the fully qualified formatter name

If you do not want to register the short name, use the full module path:

```bash
behave -f behave_modern_console_report.formatters.modern:ModernFormatter
```

## Combining with other formatters

Behave supports multiple formatters at once. For example, generate a Markdown report while showing live console output:

```bash
behave -f modern-live -o /dev/null -f behave_modern_md_report.formatter:BehaveMarkdownFormatter -o report.md
```

On Windows use `NUL` instead of `/dev/null`:

```powershell
behave -f modern-live -o NUL -f behave_modern_md_report.formatter:BehaveMarkdownFormatter -o report.md
```

## Running a single feature file

```bash
behave --format=modern features/login.feature
```

## Passing configuration options

```bash
behave --format=modern -D mcr.colors=false -D mcr.show_steps=false
```

See [configuration.md](configuration.md) for the full list of options.
