"""Tests for per-formatter configuration."""

from __future__ import annotations

from behave_modern_console_report.config import FormatterConfig
from tests.conftest import FakeBehaveConfig


def test_config_defaults() -> None:
    config = FormatterConfig("modern", FakeBehaveConfig())
    assert config.colors is True
    assert config.show_steps is True
    assert config.show_traceback is True
    assert config.show_progress is True


def test_config_formatter_specific() -> None:
    config = FormatterConfig(
        "modern",
        FakeBehaveConfig(
            {
                "mcr.modern.colors": "false",
                "mcr.modern.show_steps": "false",
                "mcr.modern.show_traceback": "false",
            }
        ),
    )
    assert config.colors is False
    assert config.show_steps is False
    assert config.show_traceback is False


def test_config_formatter_specific_without_global_fallback() -> None:
    config = FormatterConfig(
        "ci",
        FakeBehaveConfig(
            {
                "mcr.colors": "false",
                "mcr.show_progress": "false",
                "mcr.ci.show_progress": "false",
            }
        ),
    )
    assert config.colors is False
    assert config.show_progress is False


def test_config_global_show_progress_is_ignored() -> None:
    config = FormatterConfig(
        "ci",
        FakeBehaveConfig({"mcr.show_progress": "false"}),
    )
    assert config.show_progress is True


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
