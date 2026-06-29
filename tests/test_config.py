"""Tests for configuration loading."""

import os
from unittest.mock import patch

from behave_modern_console_report.config import Config, ThemeName, Verbosity
from tests.conftest import FakeBehaveConfig


def test_config_defaults() -> None:
    config = Config.from_behave(FakeBehaveConfig())
    assert config.theme == ThemeName.DEFAULT
    assert config.verbosity == Verbosity.NORMAL
    assert config.show_steps_auto is True


def test_config_from_user_data() -> None:
    behave_config = FakeBehaveConfig(
        {
            "modern_console_theme": "dark",
            "modern_console_verbosity": "verbose",
            "modern_console_compact": "true",
        }
    )
    config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.DARK
    assert config.verbosity == Verbosity.VERBOSE
    assert config.compact is True


def test_config_from_environment() -> None:
    behave_config = FakeBehaveConfig()
    env = {
        "MODERN_CONSOLE_THEME": "light",
        "MODERN_CONSOLE_VERBOSITY": "minimal",
    }
    with patch.dict(os.environ, env, clear=True):
        config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.LIGHT
    assert config.verbosity == Verbosity.MINIMAL


def test_config_user_data_overrides_environment() -> None:
    behave_config = FakeBehaveConfig({"modern_console_theme": "monochrome"})
    env = {"MODERN_CONSOLE_THEME": "dark"}
    with patch.dict(os.environ, env, clear=True):
        config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.MONOCHROME


def test_config_from_mcr_user_data() -> None:
    behave_config = FakeBehaveConfig(
        {
            "mcr.theme": "dark",
            "mcr.verbosity": "verbose",
            "mcr.compact": "true",
        }
    )
    config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.DARK
    assert config.verbosity == Verbosity.VERBOSE
    assert config.compact is True


def test_config_mcr_takes_precedence_over_legacy() -> None:
    behave_config = FakeBehaveConfig(
        {
            "mcr.theme": "dark",
            "modern_console_theme": "light",
        }
    )
    config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.DARK


def test_config_from_mcr_environment() -> None:
    behave_config = FakeBehaveConfig()
    env = {
        "MCR_THEME": "light",
        "MCR_VERBOSITY": "minimal",
    }
    with patch.dict(os.environ, env, clear=True):
        config = Config.from_behave(behave_config)
    assert config.theme == ThemeName.LIGHT
    assert config.verbosity == Verbosity.MINIMAL


def test_config_auto_show_steps() -> None:
    config = Config(verbosity=Verbosity.NORMAL, show_steps_auto=True)
    assert config.effective_show_steps() is False

    config = Config(verbosity=Verbosity.VERBOSE, show_steps_auto=True)
    assert config.effective_show_steps() is True


def test_config_ci_detection() -> None:
    behave_config = FakeBehaveConfig()
    with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
        config = Config.from_behave(behave_config)
    assert config.is_ci is True
    assert config.is_interactive is False
    assert config.colors is False


def test_config_explicit_colors_override_ci() -> None:
    behave_config = FakeBehaveConfig({"modern_console_colors": "true"})
    with patch.dict(os.environ, {"CI": "true"}, clear=True):
        config = Config.from_behave(behave_config)
    assert config.colors is True
    assert config.is_ci is True
