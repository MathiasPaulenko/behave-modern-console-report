"""Color/style helpers for the modern console formatter.

This module centralizes common color and style utilities so that themes can
remain focused on semantic intent rather than low-level Rich style values.
"""

from __future__ import annotations

from rich.style import Style
from rich.text import Text


def styled(text: str, style: Style | None = None) -> Text:
    """Create a styled Rich Text object."""
    return Text(text, style=style)


def dim(text: str) -> Text:
    """Create a dimmed Rich Text object."""
    return Text(text, style=Style(dim=True))


def bold(text: str, color: str | None = None) -> Text:
    """Create a bold Rich Text object with an optional foreground color."""
    style = Style(bold=True, color=color) if color else Style(bold=True)
    return Text(text, style=style)
