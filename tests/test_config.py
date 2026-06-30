"""Tests for per-formatter configuration."""

from __future__ import annotations

from behave_modern_console_report.config import FormatterConfig, Verbosity
from tests.conftest import FakeBehaveConfig


def test_config_defaults() -> None:
    config = FormatterConfig("modern", FakeBehaveConfig())
    assert config.colors is True
    assert config.show_steps is True
    assert config.show_traceback is True
    assert config.show_progress is True
    assert config.live is False
    assert config.verbosity == Verbosity.NORMAL


def test_config_formatter_specific() -> None:
    config = FormatterConfig(
        "modern",
        FakeBehaveConfig(
            {
                "mcr.modern.colors": "false",
                "mcr.modern.show_steps": "false",
                "mcr.modern.live": "true",
                "mcr.modern.verbosity": "verbose",
            }
        ),
    )
    assert config.colors is False
    assert config.show_steps is False
    assert config.live is True
    assert config.verbosity == Verbosity.VERBOSE


def test_config_global_fallback() -> None:
    config = FormatterConfig(
        "ci",
        FakeBehaveConfig(
            {
                "mcr.colors": "false",
                "mcr.show_progress": "false",
            }
        ),
    )
    assert config.colors is False
    assert config.show_progress is False


def test_config_formatter_specific_overrides_global() -> None:
    config = FormatterConfig(
        "ci",
        FakeBehaveConfig(
            {
                "mcr.colors": "false",
                "mcr.ci.colors": "true",
            }
        ),
    )
    assert config.colors is True


def test_config_invalid_verbosity_uses_default() -> None:
    config = FormatterConfig(
        "modern",
        FakeBehaveConfig({"mcr.modern.verbosity": "unknown"}),
    )
    assert config.verbosity == Verbosity.NORMAL
