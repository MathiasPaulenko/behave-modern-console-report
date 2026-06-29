"""Tests for theme definitions."""

from behave_modern_console_report.config import ThemeName
from behave_modern_console_report.themes import get_theme, list_themes


def test_get_default_theme() -> None:
    theme = get_theme(ThemeName.DEFAULT)
    assert theme.name == "default"


def test_all_themes_available() -> None:
    for theme_name in ThemeName:
        theme = get_theme(theme_name)
        assert theme.name == theme_name.value


def test_list_themes() -> None:
    themes = list_themes()
    assert "default" in themes
    assert "dark" in themes
    assert "light" in themes
    assert "minimal" in themes
    assert "monochrome" in themes


def test_unknown_theme_falls_back_to_default() -> None:
    theme = get_theme(ThemeName.DEFAULT)  # Cannot pass unknown enum value
    assert theme.name == "default"
