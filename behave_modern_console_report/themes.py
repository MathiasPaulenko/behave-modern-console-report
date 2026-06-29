"""Theme definitions for the modern console formatter.

A Theme is a collection of Rich styles keyed by semantic role. New themes can
be added by extending the ``get_theme`` mapping without changing rendering
logic, making the formatter easy to customize.
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.style import Style

from behave_modern_console_report.config import ThemeName


@dataclass
class Theme:
    """Semantic theme styles used by the renderer."""

    name: str
    passed: Style
    failed: Style
    skipped: Style
    undefined: Style
    pending: Style
    running: Style
    duration: Style
    header: Style
    text: Style
    muted: Style
    progress_fill: Style
    progress_empty: Style
    border: Style


def _default_theme() -> Theme:
    return Theme(
        name="default",
        passed=Style(color="green", bold=True),
        failed=Style(color="red", bold=True),
        skipped=Style(color="yellow"),
        undefined=Style(color="magenta", bold=True),
        pending=Style(color="bright_yellow"),
        running=Style(color="cyan"),
        duration=Style(color="bright_black"),
        header=Style(color="cyan", bold=True),
        text=Style(),
        muted=Style(color="bright_black", dim=True),
        progress_fill=Style(color="green"),
        progress_empty=Style(color="bright_black"),
        border=Style(color="bright_black"),
    )


def _dark_theme() -> Theme:
    return Theme(
        name="dark",
        passed=Style(color="green"),
        failed=Style(color="red"),
        skipped=Style(color="yellow"),
        undefined=Style(color="magenta"),
        pending=Style(color="bright_yellow"),
        running=Style(color="cyan"),
        duration=Style(color="white"),
        header=Style(color="cyan", bold=True),
        text=Style(color="white"),
        muted=Style(color="bright_black"),
        progress_fill=Style(color="green"),
        progress_empty=Style(color="black"),
        border=Style(color="bright_black"),
    )


def _light_theme() -> Theme:
    return Theme(
        name="light",
        passed=Style(color="dark_green"),
        failed=Style(color="dark_red"),
        skipped=Style(color="dark_goldenrod"),
        undefined=Style(color="dark_magenta"),
        pending=Style(color="dark_orange3"),
        running=Style(color="dark_blue"),
        duration=Style(color="black"),
        header=Style(color="dark_blue", bold=True),
        text=Style(color="black"),
        muted=Style(color="grey70"),
        progress_fill=Style(color="dark_green"),
        progress_empty=Style(color="grey70"),
        border=Style(color="grey70"),
    )


def _minimal_theme() -> Theme:
    return Theme(
        name="minimal",
        passed=Style(),
        failed=Style(),
        skipped=Style(),
        undefined=Style(),
        pending=Style(),
        running=Style(),
        duration=Style(dim=True),
        header=Style(bold=True),
        text=Style(),
        muted=Style(dim=True),
        progress_fill=Style(),
        progress_empty=Style(dim=True),
        border=Style(dim=True),
    )


def _monochrome_theme() -> Theme:
    return Theme(
        name="monochrome",
        passed=Style(color="white"),
        failed=Style(color="white"),
        skipped=Style(color="white"),
        undefined=Style(color="white"),
        pending=Style(color="white"),
        running=Style(color="white"),
        duration=Style(color="white", dim=True),
        header=Style(color="white", bold=True),
        text=Style(color="white"),
        muted=Style(color="white", dim=True),
        progress_fill=Style(color="white"),
        progress_empty=Style(color="white", dim=True),
        border=Style(color="white", dim=True),
    )


_THEMES: dict[ThemeName, Theme] = {
    ThemeName.DEFAULT: _default_theme(),
    ThemeName.DARK: _dark_theme(),
    ThemeName.LIGHT: _light_theme(),
    ThemeName.MINIMAL: _minimal_theme(),
    ThemeName.MONOCHROME: _monochrome_theme(),
}


def get_theme(name: ThemeName) -> Theme:
    """Return a Theme instance by name.

    Args:
        name: Built-in theme name.

    Returns:
        Theme instance. Unknown names fall back to the default theme.
    """
    return _THEMES.get(name, _default_theme())


def list_themes() -> list[str]:
    """Return a list of available theme names."""
    return [theme.name for theme in _THEMES.values()]
