# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-03

### Fixed
- **`-o`/`--outfile` ignored by all formatters**: `BaseFormatter` now calls `open()` on the stream opener at construction. Behave opens output streams lazily, so the formatter previously saw `stream=None` and fell back to `sys.stdout` — the output file stayed empty and the report leaked to the console.
- **Output stream never closed**: `BaseFormatter.close()` now calls `close_stream()` so `-o` files are properly closed.
- **`progress` crash with `-o`**: `ProgressFormatter` no longer crashes with `AttributeError: 'NoneType' object has no attribute 'write'` when a file output is configured.
- **`UnicodeEncodeError` on non-UTF-8 output (Windows)**: Output is wrapped in a UTF-8 `TextIOWrapper` when the underlying binary buffer is reachable, so icons (`✓`, `✗`, `⏭`, `█`, `░`, `⏱`, `🚀`) no longer crash on cp1252/cp850 terminals, pipes, or files — even with `mcr.colors=false`.
- **ANSI codes in piped/file output**: `Console` no longer forces terminal mode; colors are auto-disabled on non-TTY output. `mcr.colors=false` is still honored explicitly.
- **Per-formatter config namespace mismatch**: `mcr.<formatter>.<key>` now uses the registered formatter name (`modern-console`, `modern-console-live`) instead of the internal names (`modern`, `modern-live`), matching the documentation.
- **Scenarios with no step results never counted**: `Collector.finish()` now finalizes leftover non-terminal scenarios using Behave's final status (unrun ones count as skipped).
- **`Feature.duration` never computed**: Now aggregated from scenario durations.
- **`modern-console-live` on non-terminals**: Falls back to printing the final report once instead of dumping a frame per refresh.
- **`failures_block` misleading location label**: Now prints `Feature: <name>, scenario at line <n>` (the line is the scenario's), and tracebacks are indented consistently.
- **`colorama` dependency removed**: The progress formatter used only ANSI constants; `colorama` was never initialized anyway.

### Changed
- **Removed `[project.entry-points."behave.formatters"]`**: Behave does not read entry points for formatters — registration works via `[behave.formatters]` in `behave.ini` or `module:Class` names, as documented.
- Classifier updated to `Development Status :: 5 - Production/Stable`.
- Added `py.typed` marker so the `Typing :: Typed` classifier is honored.
- Ruff rule `TCH` renamed to `TC` (requires `ruff>=0.8.0`).

### Added
- MkDocs configuration (`mkdocs.yml`) and `docs/index.md` landing page; install `.[docs]` to build.
- Tests covering `-o` file output, Unicode-safe streams, `modern-console-live`, and leftover scenarios.
- CI smoke step running the example features through the formatters.

### Documentation
- README formatter output examples now match the real output (`log`, `ci`, `minimal`).
- `examples/README.md` rewritten: removed references to nonexistent `modern_console_*` options and the old `modern` formatter name.
- `docs/configuration.md` documents the exact `mcr.<formatter>.*` namespaces.
- SECURITY.md supported versions fixed (1.2.x), placeholder `example.com` contacts replaced with GitHub links.
- `docs/contributing.md` now points to the root `CONTRIBUTING.md` (single source of truth).
- Windows `NUL` alternative added where `/dev/null` is used.

## [1.2.0] - 2026-08-10

### Fixed
- **Step stuck in "running" state**: `Collector.set_running()` no longer sets the scenario to RUNNING when all steps are already terminal (e.g. skipped). `Collector.update_result()` now always recalculates scenario/feature status, correcting any stale RUNNING state.
- **Scenario/Feature status incorrectly UNTESTED for in-progress items**: `Scenario.update_status()` and `Feature.update_status()` now return RUNNING instead of UNTESTED when some steps/scenarios are terminal and others are not yet started.
- **Mixed PASSED+SKIPPED aggregation**: `Scenario.update_status()` and `Feature.update_status()` now correctly return PASSED (not UNTESTED) when steps/scenarios are a mix of PASSED and SKIPPED.
- **Missing PENDING in status aggregation**: `Scenario.update_status()`, `Feature.update_status()`, and `Execution.add_scenario_result()` now handle PENDING status correctly.
- **Missing PENDING and Undefined counts in summaries**: All formatter summaries (`render.summary_block`, `Minimal`, `CI`, `Log`, `Progress`) now include PENDING and Undefined scenario counts when applicable.
- **BaseFormatter stream initialization**: `BaseFormatter.__init__` now uses `self.stream` (opened by `Formatter.__init__`) instead of the raw `StreamOpener`, preventing fallback to `sys.stdout` when file output is intended.
- **ProgressFormatter double stream open**: `ProgressFormatter.__init__` no longer calls `stream.open()` a second time; it reuses `self._stream` from the base class.
- **Defensive guards for None values**: `Collector.add_feature()` and `Collector.add_scenario()` now handle `None` description/tags from Behave without crashing.
- **Error extraction with exception**: `_extract_error()` now uses the exception type name when `exception` is set but `error_message` is empty.
- **`Status.from_behave` with None and non-string types**: Now handles `None` status and enum-like objects with a `.name` attribute. Maps `"running"` string to `Status.RUNNING`.
- **`format_duration` with inf/nan**: Now guards against non-finite float values that would crash `int()` conversion.
- **`failures_block` empty error type**: No longer prints an empty error type line when `error.type` is an empty string.
- **Cleanup passes in formatters**: `CI`, `Log`, and `Minimal` formatters now print any unprinted terminal scenarios in `on_close()`.

### Changed
- **Breaking**: Renamed entry point `modern` → `modern-console` to avoid collision with `behave-modern-html-report`.
- **Breaking**: Renamed entry point `modern-live` → `modern-console-live` for naming consistency.
- Updated README, docs, and examples to reflect the new entry point names.
- Users must update `behave.ini` and CLI flags from `--format=modern` to `--format=modern-console`.

## [1.0.1] - 2026-07-01

### Fixed
- Progress formatter now updates per scenario instead of per step, reducing flickering.
- Progress formatter detects TTY and uses in-place updates only on real terminals.
- Progress formatter no longer interleaves with logging output when using `--no-logcapture`.

### Changed
- README: added all formatter registrations to the Quick start `behave.ini` example.
- README: added Features section, formatter examples, and CI/CD section.

## [1.0.0] - 2026-06-30

### Added
- Six formatters: `modern`, `modern-live`, `progress`, `log`, `ci`, and `minimal`.
- Layered architecture: base formatter, collector, models, render helpers.
- Per-formatter configuration via `mcr.<formatter>.<key>` with global `mcr.<key>` fallback.
- Colored status icons, progress bars, and execution summaries.
- Failure diagnostics with error type, message, and optional traceback.
- Configuration via Behave user data (`-D key=value`) or `behave.ini`.
- Unit tests for models, collector, config, utils, and formatter output.
- GitHub Actions CI workflow (lint, test, packaging).
- GitHub Actions release workflow (automatic PyPI publishing via Trusted Publishing).
- Documentation: README, configuration, usage, CI/CD, architecture, and contributing guides.
- MIT license and PyPI-ready packaging.

## [0.1.0] - 2026-06-29

### Added
- Initial development release.
