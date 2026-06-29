# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-29

### Added
- Initial release of `behave-modern-console-report`.
- Real-time terminal formatter for Behave using the Rich library.
- Layered architecture: formatter, collector, models, renderer, and console.
- Support for verbosity levels: minimal, normal, verbose, and debug.
- Built-in themes: default, dark, light, minimal, and monochrome.
- Automatic CI/CD detection with non-animated, log-friendly output.
- Progress bar, live scenario status, and end-of-run summary.
- Failure diagnostics with scenario name, error type, and message.
- Configuration via Behave user data and environment variables.
- Comprehensive unit tests, integration tests, and golden snapshot tests.
- GitHub Actions workflows for lint, tests, coverage, and packaging.
- MIT license and PyPI-ready packaging.
