# Configuration Reference

Configuration can be provided via Behave user data (`-D key=value`) or
environment variables. User data takes precedence over environment variables.

## Options

| Option | Environment Variable | Default | Description |
| --- | --- | --- | --- |
| `modern_console_theme` | `MODERN_CONSOLE_THEME` | `default` | Output theme. Available: `default`, `dark`, `light`, `minimal`, `monochrome`. |
| `modern_console_verbosity` | `MODERN_CONSOLE_VERBOSITY` | `normal` | Output verbosity. Available: `minimal`, `normal`, `verbose`, `debug`. |
| `modern_console_colors` | `MODERN_CONSOLE_COLORS` | `auto` | `auto`, `true`, or `false`. In CI, `auto` defaults to `false`. |
| `modern_console_compact` | `MODERN_CONSOLE_COMPACT` | `false` | Show only the most recent scenarios in the live list. |
| `modern_console_show_steps` | `MODERN_CONSOLE_SHOW_STEPS` | `auto` | `auto` enables step output for `verbose` and `debug`. |
| `modern_console_show_durations` | `MODERN_CONSOLE_SHOW_DURATIONS` | `true` | Show scenario and step durations. |
| `modern_console_show_progress` | `MODERN_CONSOLE_SHOW_PROGRESS` | `true` | Show the progress bar. |
| `modern_console_show_environment` | `MODERN_CONSOLE_SHOW_ENVIRONMENT` | `false` | Show environment information. |
| `modern_console_show_traceback` | `MODERN_CONSOLE_SHOW_TRACEBACK` | `true` | Show full tracebacks for failed steps. |

## CI Detection

The formatter detects common CI environments by checking these environment
variables:

- `CI`
- `GITHUB_ACTIONS`
- `GITLAB_CI`
- `CIRCLECI`
- `TRAVIS`
- `JENKINS_URL`
- `BUILDKITE`
- `DRONE`
- `TF_BUILD`
- `APPVEYOR`
- `AZURE_DEVOPS`

When a CI environment is detected, animations are disabled, output is
simplified, and colors default to off unless explicitly enabled.

## Examples

Run with the dark theme and verbose output:

```bash
behave --format=modern -D modern_console_theme=dark -D modern_console_verbosity=verbose
```

Disable colors and progress for a CI log:

```bash
behave --format=modern -D modern_console_colors=false -D modern_console_show_progress=false
```

Set options via environment variables:

```bash
export MODERN_CONSOLE_THEME=minimal
export MODERN_CONSOLE_VERBOSITY=verbose
behave --format=modern
```
