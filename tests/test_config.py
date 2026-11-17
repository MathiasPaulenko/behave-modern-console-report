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


def test_config_registered_formatter_name() -> None:
    """Per-formatter keys use the registered name (e.g. modern-console)."""
    config = FormatterConfig(
        "modern-console",
        FakeBehaveConfig({"mcr.modern-console.colors": "false"}),
    )
    assert config.colors is False


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


def test_config_non_dict_userdata() -> None:
    """Regression: a non-dict userdata attribute must not crash the config."""
    behave_config = type("Config", (), {"userdata": "not-a-dict"})()
    config = FormatterConfig("ci", behave_config)
    assert config.colors is True
    assert config.show_progress is True


def test_config_missing_userdata_attribute() -> None:
    """A behave config without userdata falls back to defaults."""
    behave_config = type("Config", (), {})()
    config = FormatterConfig("ci", behave_config)
    assert config.colors is True


def test_config_bool_values_with_whitespace() -> None:
    """Regression: -D values with surrounding whitespace must still parse."""
    config = FormatterConfig(
        "ci",
        FakeBehaveConfig({"mcr.colors": " false ", "mcr.ci.show_steps": " true "}),
    )
    assert config.colors is False
    assert config.show_steps is True


def test_config_bool_variants() -> None:
    """Truthy spellings: 1, yes, on; anything else is False."""
    for truthy in ("1", "yes", "on", "TRUE"):
        config = FormatterConfig("ci", FakeBehaveConfig({"mcr.colors": truthy}))
        assert config.colors is True, truthy
    for falsy in ("0", "no", "off", "FALSE", "banana"):
        config = FormatterConfig("ci", FakeBehaveConfig({"mcr.colors": falsy}))
        assert config.colors is False, falsy
