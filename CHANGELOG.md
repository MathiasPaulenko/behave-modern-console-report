# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
