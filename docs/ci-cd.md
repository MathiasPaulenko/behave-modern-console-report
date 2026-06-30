# CI/CD integration

The console formatters are designed to work well in CI/CD pipelines. The `ci` formatter is specifically built for CI output with colored status tags and a compact summary.

## Choosing a formatter for CI

| Formatter | CI suitability |
| --- | --- |
| `ci` | Best for CI — compact, colored status tags, end-of-run failure summary. |
| `log` | Good for CI — timestamped lines, no live updates. |
| `minimal` | Good for CI — plain text, no colors, minimal noise. |
| `modern` | Works in CI but designed for interactive terminals. |
| `modern-live` | Not recommended for CI — uses Rich Live which may not render correctly. |
| `progress` | Not recommended for CI — uses in-place line updates. |

## GitHub Actions

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

### Disabling colors in CI

```bash
behave --format=ci -D mcr.colors=false
```

### Hiding step details for compact output

```bash
behave --format=ci -D mcr.show_steps=false
```

### Hiding the progress bar

```bash
behave --format=ci -D mcr.ci.show_progress=false
```

## GitLab CI

```yaml
test:
  image: python:3.12
  script:
    - pip install -e ".[dev]"
    - behave --format=ci -D mcr.colors=false
```

## Azure DevOps

```yaml
steps:
  - script: |
      pip install -e ".[dev]"
      behave --format=ci -D mcr.colors=false
    displayName: Run Behave tests
```

## Jenkins

```bash
pip install -e ".[dev]"
behave --format=ci -D mcr.colors=false
```

## Combining with the Markdown report

You can show console output and generate a Markdown report at the same time:

```bash
behave -f ci -o /dev/null -f behave_modern_md_report.formatter:BehaveMarkdownFormatter -o report.md
```
